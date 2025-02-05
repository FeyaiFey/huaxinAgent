from typing import Dict, Any
import os
from datetime import datetime
from .base import BaseRule
from utils.logger import get_logger

logger = get_logger(__name__)

class TestReportRule(BaseRule):
    """测试报告规则"""
    
    def process(self, email_data: Dict[str, Any]) -> bool:
        """
        处理测试报告邮件
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
            
            # 获取日期信息用于文件名
            date_str = datetime.now().strftime('%Y%m%d')
            
            # 保存附件
            attachments = email_data.get('attachments', [])
            for attachment in attachments:
                filename = attachment.get('filename')
                content = attachment.get('content')
                if filename and content:
                    # 添加日期和供应商信息到文件名
                    name, ext = os.path.splitext(filename)
                    new_filename = f"{name}_{self.supplier}_{date_str}{ext}"
                    file_path = os.path.join(save_dir, new_filename)
                    
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    logger.info(f"保存测试报告成功: {file_path}")
            
            # 标记为已读
            if self.actions.get('mark_as_read'):
                email_data['mark_as_read'] = True
                
            return True
            
        except Exception as e:
            logger.error(f"处理测试报告邮件失败: {str(e)}", exc_info=True)
            return False