# 提供邮件处理的一些方法

import chardet
import email
import os
from pathlib import Path
from email import message
from imaplib import IMAP4_SSL

from email.header import decode_header
from typing import Dict, List, Tuple, Union, Optional

from utils.logger import Logger

class EmailHelper:
    def __init__(self, imap: IMAP4_SSL):
        self.logger = Logger(__name__)
        self.imap = imap

    def decode_text(self, text: Union[str, bytes], charset: Optional[str] = None) -> str:
        """
        解码文本内容
        
        处理各种编码情况，优先使用指定的字符集，如果失败则尝试自动检测编码
        
        参数:
            text: 要解码的文本
            charset: 字符集（可选）
            
        返回:
            str: 解码后的文本
        """
        if isinstance(text, bytes):
            if not charset:
                detected = chardet.detect(text)
                charset = detected['encoding']
                self.logger.debug(f"检测到文本编码: {charset}")
            try:
                return text.decode(charset or 'utf-8', errors='ignore')
            except Exception as e:
                self.logger.warning(f"使用 {charset} 解码失败: {str(e)}，尝试使用 utf-8")
                return text.decode('utf-8', errors='ignore')
        return text
    
    def get_email_addresses(self, msg: message.Message, header_name: str) -> List[str]:
        """
        获取邮件地址列表
        
        从邮件头部提取邮件地址（发件人、收件人或抄送人）
        
        参数:
            msg: 邮件消息对象
            header_name: 头部字段名（from/to/cc）
            
        返回:
            list: 邮件地址列表
        """
        values = msg.get_all(header_name, [])
        addresses = email.utils.getaddresses(values)
        return [addr[1] for addr in addresses if addr[1]]

    def decode_header_value(self, value: Optional[str]) -> str:
        """
        解码邮件头部值
        
        处理可能包含多个编码部分的邮件头部值
        
        参数:
            value: 要解码的头部值
            
        返回:
            str: 解码后的文本
        """
        if not value:
            return ""
            
        decoded_list = decode_header(value)
        result = []
        
        for text, charset in decoded_list:
            if isinstance(text, bytes):
                text = self._decode_bytes(text, charset)
            result.append(str(text))
            
        return "".join(result)

    def _decode_bytes(self, text: bytes, charset: Optional[str]) -> str:
        """解码字节数据"""
        try:
            if charset:
                return text.decode(charset)
            detected = chardet.detect(text)
            return text.decode(detected['encoding'] or 'utf-8', errors='ignore')
        except Exception as e:
            self.logger.warning(f"解码头部值失败: {str(e)}，使用 utf-8")
            return text.decode('utf-8', errors='ignore')
        
    def normalize_email_id(self, email_id: Union[str, bytes]) -> bytes:
        """标准化邮件ID格式"""
        return email_id if isinstance(email_id, bytes) else str(email_id).encode()
    
    def fetch_email(self, email_id: bytes) -> message.Message:
        """获取邮件内容"""
        _, msg_data = self.imap.fetch(email_id, '(BODY.PEEK[])')
        email_body = msg_data[0][1]
        return email.message_from_bytes(email_body)
    
    # 重要: 解析邮件数据
    def parse_email_data(self, msg: message.Message, email_id: bytes) -> Dict:
        """解析邮件数据"""
        subject = self.decode_header_value(msg["Subject"])
        from_addr = self.get_email_addresses(msg, 'from')[0] if self.get_email_addresses(msg, 'from') else ""
        to_addrs = self.get_email_addresses(msg, 'to')
        cc_addrs = self.get_email_addresses(msg, 'cc')
        
        self.logger.debug(f"邮件信息 - 主题: {subject}")
        
        return {
            'id': email_id.decode(),
            'from': from_addr,
            'to': to_addrs,
            'cc': cc_addrs,
            'subject': subject
        }
    
    def _is_attachment(self, part: message.Message) -> bool:
        """检查是否为附件"""
        return (part.get_content_maintype() != 'multipart' and 
                part.get('Content-Disposition') is not None)

    def _get_attachment_filename(self, part: message.Message) -> Optional[str]:
        """获取附件文件名"""
        filename = part.get_filename()
        if filename:
            return self.decode_header_value(filename)
        return None
    
    def _save_attachment(self, part: message.Message, folder: str) -> bool:
        """保存附件"""
        filename = self._get_attachment_filename(part)
        if filename:
            filepath = os.path.join(folder, filename)
            with open(filepath, 'wb') as f:
                f.write(part.get_payload(decode=True))
            return True
        return False
    
    def _save_attachment_file(self, part: message.Message, filename: str,
                            email_id: bytes, folder_path: Path) -> Optional[Path]:
        """保存附件文件"""
        try:
            self.logger.debug(f"处理附件: {filename}")
            
            # 确保folder_path是Path对象
            folder_path = Path(folder_path)
            
            # 确保目录存在
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # 构建文件路径
            filepath = folder_path.joinpath(filename)
            
            # 检查文件是否已存在
            if filepath.exists():
                self.logger.debug(f"附件已存在，跳过下载: {filename}")
                return filepath
            
            # 保存文件
            with filepath.open('wb') as f:
                f.write(part.get_payload(decode=True))
                
            self.logger.info(f"附件已保存: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"保存附件失败: {str(e)}")
            return None

    
    def save_attachments(self, msg: message.Message, email_id: bytes, 
                        folder_path: Path) -> List[str]:
        """
        保存邮件附件
        
        遍历邮件的所有部分，保存附件到指定文件夹
        
        参数:
            msg: 邮件消息对象
            email_id: 邮件ID
            folder_path: 保存文件夹路径
            
        返回:
            list: 保存的附件文件路径列表
        """
        saved_files = []
        
        for part in msg.walk():
            if not self._is_attachment(part):
                continue
                
            filename = self._get_attachment_filename(part)
            if filename:
                filepath = self._save_attachment_file(part, filename, email_id, folder_path)
                if filepath:
                    saved_files.append(str(filepath))
                    
        return saved_files

    
    def mark_email_as_read(self, email_id: Union[str, bytes]) -> bool:
        """
        标记邮件为已读
        
        参数:
            email_id: 邮件ID
            
        返回:
            bool: 是否成功标记
            
        异常:
            ConnectionError: 未连接到服务器时抛出
        """
        try:
            email_id = self.normalize_email_id(email_id)
            self.imap.store(email_id, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            self.logger.error(f"标记邮件为已读失败: {str(e)}")
            return False
    
