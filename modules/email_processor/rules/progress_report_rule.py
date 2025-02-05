from typing import Dict, Any
import os
from datetime import datetime
import pandas as pd
from .base import BaseRule
from utils.logger import get_logger

logger = get_logger(__name__)

class ProgressReportRule(BaseRule):
    """进度表规则"""
    
    def process(self, email_data: Dict[str, Any]) -> bool:
        """
        处理进度表邮件
        Args:
            email_data: 邮件数据字典
        Returns:
            处理是否成功
        """
        try:
            if not self.actions.get('save_attachment'):
                return True
                
            # 获取附件保存路径
            save_dir = self.actions.get('attachment_folder', '')
            if not save_dir:
                logger.error(f"未配置附件保存路径: {self.name}")
                return False
                
            # 创建保存目录
            os.makedirs(save_dir, exist_ok=True)
            
            # 获取日期信息
            date_str = datetime.now().strftime('%Y%m%d')
            
            # 保存并处理附件
            attachments = email_data.get('attachments', [])
            for attachment in attachments:
                filename = attachment.get('filename')
                content = attachment.get('content')
                if filename and content:
                    # 添加日期和供应商信息到文件名
                    name, ext = os.path.splitext(filename)
                    new_filename = f"{name}_{self.supplier}_{date_str}{ext}"
                    file_path = os.path.join(save_dir, new_filename)
                    
                    # 保存原始文件
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    logger.info(f"保存进度表成功: {file_path}")
                    
                    # 如果是Excel文件，尝试进行数据处理
                    if ext.lower() in ['.xls', '.xlsx']:
                        try:
                            # 读取Excel文件
                            df = pd.read_excel(file_path)
                            
                            # 处理数据（可以根据需要添加具体的处理逻辑）
                            processed_file = os.path.join(
                                save_dir, 
                                f"{name}_{self.supplier}_{date_str}_processed{ext}"
                            )
                            df.to_excel(processed_file, index=False)
                            logger.info(f"处理进度表成功: {processed_file}")
                            
                        except Exception as e:
                            logger.error(f"处理Excel文件失败: {str(e)}", exc_info=True)
            
            # 标记为已读
            if self.actions.get('mark_as_read'):
                email_data['mark_as_read'] = True
                
            return True
            
        except Exception as e:
            logger.error(f"处理进度表邮件失败: {str(e)}", exc_info=True)
            return False