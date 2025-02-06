"""
邮件处理核心模块
负责协调邮件检查、规则应用和文件处理的整体流程
"""

from typing import Dict, Any

from utils.logger import Logger
from infrastructure.email_client import EmailClient
from modules.file_processor.delivery_handler import DeliveryHandler
# from modules.erp_integration.adapter import ERPAdapter

class EmailProcessor:
    """邮件处理器核心类"""
    
    def __init__(self):
        """初始化邮件处理器"""
        self.logger = Logger(__name__)
        self._init_email_client()
        self.delivery_handler = DeliveryHandler()
        # self.erp_adapter = ERPAdapter()

    def _init_email_client(self):
        """初始化邮件客户端"""
        self.email_client = EmailClient('config/email_config.yaml')
        self.email_client.connect()
        self.imap = self.email_client.imap

    def process_unread_emails(self) -> Dict[str, int]:
        """
        处理所有未读邮件
        Returns:
            处理统计信息
        """
        stats = {
            'total': 0,
            'processed': 0,
            'failed': 0,
            'attachments': 0
        }
        
        try:
            # 获取所有未读邮件
            unread_emails = self.email_client.get_unread_emails()
            stats['total'] = len(unread_emails)
            
            # 处理每封邮件
            for email_id in unread_emails:
                try:
                    # 应用规则引擎，得到匹配结果
                    match_result = self.email_client.process_email(email_id)
                    
                    # 检查是否有匹配结果
                    if not match_result:
                        self.logger.debug("邮件不匹配任何规则，跳过处理")
                        continue
                        
                    # 统计附件数
                    attachments = match_result.get('attachments', [])
                    if attachments:
                        stats['attachments'] += len(attachments)
                    
                    # 根据匹配结果，处理附件
                    category = match_result.get('category')
                    if category == '封装送货单' and attachments:
                        result = self.delivery_handler.process_delivery_excel(match_result)
                        stats['processed'] += 1
                        self.logger.debug(f"处理结果: {result}")

                    # TODO: 处理其他规则 封装进度表\fab进度表\测试报告\
                        
                except Exception as e:
                    stats['failed'] += 1
                    self.logger.error(f"处理邮件失败: {str(e)}", exc_info=True)
                    continue
                    
            self.logger.info(
                f"邮件处理完成: 总数 {stats['total']}, "
                f"成功 {stats['processed']}, "
                f"失败 {stats['failed']}, "
                f"附件 {stats['attachments']}"
            )
            return stats
            
        except Exception as e:
            self.logger.error(f"邮件处理过程发生错误: {str(e)}", exc_info=True)
            raise

        finally:
            self.email_client.disconnect()
            
    def _process_attachment(self, attachment: Dict[str, Any], rule_type: str) -> None:
        """
        处理单个附件
        Args:
            attachment: 附件信息
            rule_type: 规则类型
        """
        try:
            # 根据规则类型处理附件
            if rule_type == 'delivery_note':
                self.excel_processor.process_delivery_note(attachment)
            elif rule_type == 'progress_report':
                self.excel_processor.process_progress_report(attachment)
            elif rule_type == 'test_report':
                self.excel_processor.process_test_report(attachment)
            else:
                self.logger.warning(f"未知的规则类型: {rule_type}")
                
        except Exception as e:
            self.logger.error(f"处理附件失败: {str(e)}", exc_info=True)
            raise 