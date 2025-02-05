from typing import Dict, Any
import os
from .base import BaseRule
from utils.logger import get_logger

logger = get_logger(__name__)

class DeliveryNoteRule(BaseRule):
    """封装送货单规则"""
    
    def process(self, email_data: Dict[str, Any]) -> bool:
        """
        处理封装送货单邮件
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
            
            # 保存附件
            attachments = email_data.get('attachments', [])
            for attachment in attachments:
                filename = attachment.get('filename')
                content = attachment.get('content')
                if filename and content:
                    file_path = os.path.join(save_dir, filename)
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    logger.info(f"保存附件成功: {file_path}")
            
            # 标记为已读
            if self.actions.get('mark_as_read'):
                email_data['mark_as_read'] = True
                
            return True
            
        except Exception as e:
            logger.error(f"处理封装送货单邮件失败: {str(e)}", exc_info=True)
            return False