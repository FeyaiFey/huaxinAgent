import imaplib
import email
from email import message
import os
import re
from email.header import decode_header
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime

from modules.email_processor.rules.engine import RuleEngine
from utils.emailHelper import EmailHelper
from utils.logger import Logger
from utils.retry import retry_network, RetryError
from utils.helpers import load_yaml, ensure_dir, get_env_var
from utils.cache import cache_5min


class IMAPEmailClient:
    """IMAP邮件客户端"""
    
    def __init__(self, config_path: str):
        """
        初始化邮件客户端
        Args:
            config_path: 配置文件路径
        """
        self.logger = Logger(__name__)
        self.config = self._load_config(config_path)
        self.rule_engine = RuleEngine(self.config['rules_file'])
        self.imap = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        Args:
            config_path: 配置文件路径
        Returns:
            配置信息
        """
        try:
            config = load_yaml(config_path)
            # 替换环境变量
            for key, value in config.items():
                if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                    env_var = value[2:-1]
                    config[key] = get_env_var(env_var, value)
            return config
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}")
            raise
    
    @retry_network
    def connect(self) -> None:
        """连接IMAP服务器"""
        try:
            if self.config.get('use_ssl', True):
                self.imap = imaplib.IMAP4_SSL(
                    self.config['imap_server'],
                    int(self.config.get('imap_port', 993))
                )
            else:
                self.imap = imaplib.IMAP4(
                    self.config['imap_server'],
                    int(self.config.get('imap_port', 143))
                )
            self.imap.login(self.config['email'], self.config['password'])
            self.logger.info(f"成功连接到IMAP服务器: {self.config['imap_server']}")
        except Exception as e:
            self.logger.error(f"连接IMAP服务器失败: {str(e)}")
            raise
    
    def check_connection(self) -> None:
        """检查IMAP连接状态"""
        if not self.imap:
            self.logger.error("未连接到邮件服务器")
            raise ConnectionError("未连接到邮件服务器")
    
    def disconnect(self) -> None:
        """断开IMAP连接"""
        if self.imap:
            try:
                self.imap.logout()
                self.logger.info("已断开IMAP连接")
            except Exception as e:
                self.logger.error(f"断开IMAP连接失败: {str(e)}")

    @retry_network
    def get_unread_emails(self) -> List[bytes]:
        """
        获取未读邮件列表
        
        返回:
            list: 未读邮件ID列表
            
        异常:
            ConnectionError: 未连接到服务器时抛出
        """
        self.check_connection()

        self.logger.info("开始获取未读邮件...")

        try:
            status, _ = self.imap.select('INBOX')
            if status != 'OK':
                raise Exception(f"无法选择收件箱，状态: {status}")
            status, messages = self.imap.search(None, 'UNSEEN')
            if status != 'OK':
                raise Exception(f"无法搜索未读邮件，状态: {status}")
            email_ids = messages[0].split()
            self.logger.info(f"找到 {len(email_ids)} 封未读邮件")
            return email_ids
        except Exception as e:
            self.logger.error(f"获取未读邮件失败: {str(e)}")
            raise
    
    def process_email(self, email_id: Union[str, bytes]) -> bool:
        """
        处理单个邮件
        
        获取邮件内容，应用规则，处理附件，设置已读状态
        
        参数:
            email_id: 邮件ID
            
        返回:
            bool: 处理结果，True表示处理成功，False表示处理失败
            
        异常:
            RuntimeError: 处理失败时抛出

        email_data: 邮件数据字典
        {
            'from': 发件人
            'to': 收件人
            'cc': 抄送人
            'subject': 主题
        }
        """
        self.check_connection()

        email_helper = EmailHelper(self.imap)

        email_id = email_helper.normalize_email_id(email_id)
        msg = email_helper.fetch_email(email_id)

        try:
            # 解析邮件信息
            email_data = email_helper.parse_email_data(msg, email_id)
            
            # 使用规则引擎匹配邮件
            match_result = self.rule_engine.apply_rules(email_data)

            category = match_result['category']
            if category == '未分类':
                self.logger.info(f"邮件不匹配任何规则，保持未读状态: {email_data['subject']}")
                return True

            # TODO 处理邮件类 核心
            self.logger.info("处理邮件待开发!")
            
            
            # 标记为已读
            if match_result['actions'].get('mark_as_read', True):
                email_helper.mark_email_as_read(email_id)

            self.logger.info(f"邮件处理完成: [{category}] {email_data['subject']}")
            return True
            
        except Exception as e:
            self.logger.error(f"处理邮件失败: {str(e)}")
            return False