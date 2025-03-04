"""
邮件处理核心模块
负责协调邮件检查、规则应用和文件处理的整体流程
"""

from typing import Dict, Any

from utils.logger import Logger
from infrastructure.email_client import EmailClient
from modules.file_processor.excel_handler import ExcelHandler
from bll.wip_fab import WipFabBLL
from bll.wip_assy import WipAssyBLL
from modules.erp_integration.workflows.receipt import ReceiptErp

class EmailProcessor:
    """邮件处理器核心类"""
    
    def __init__(self):
        """初始化邮件处理器"""
        self.logger = Logger(__name__)
        self._init_email_client()
        self.excel_handler = ExcelHandler()
        self.wip_fab_bll = WipFabBLL()
        self.wip_assy_bll = WipAssyBLL()

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
                    self.logger.debug(f"匹配结果: {match_result}")
                    
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
                        result = self.excel_handler.process_excel(match_result)
                        stats['processed'] += 1
                        self.logger.debug(f"处理结果: {result}")
                        try:
                            receipt_handler = ReceiptErp()
                            # 从result中提取必要的数据
                            # result是一个字典，key是日期，value是该日期的送货单数据列表
                            for delivery_date, delivery_items in result.items():
                                supplier = match_result.get('supplier')
                                success = receipt_handler.process_delivery_data(
                                    date=delivery_date,
                                    supplier=supplier,
                                    data=delivery_items
                                )
                                if success:
                                    self.logger.info(f"{supplier}送货单数据录入E10成功！")
                                else:
                                    self.logger.error(f"{supplier}送货单数据录入E10失败：返回值为False")
                                    stats['failed'] += 1
                                    break
                        except Exception as e:
                            self.logger.error(f"{match_result.get('supplier')}送货单数据录入E10失败：{str(e)}", exc_info=True)
                            stats['failed'] += 1
                        continue
                    
                    if category == '封装进度表' and attachments:
                        result = self.excel_handler.process_excel(match_result)
                        if result is None:
                            stats['failed'] += 1
                            self.logger.debug("该封装进度表内容可能为空或格式错误，跳过处理")
                            continue
                        stats['processed'] += 1
                        self.logger.debug(f"处理结果: {result}")
                        self.wip_assy_bll.update_supplier_progress(result.to_dict(orient="records"))
                        continue

                    if category == '晶圆进度表' and attachments:
                        result = self.excel_handler.process_excel(match_result)
                        if result is None:
                            stats['failed'] += 1
                            self.logger.debug("该晶圆进度表内容可能为空或格式错误，跳过处理")
                            continue
                        stats['processed'] += 1
                        self.logger.debug(f"处理结果: {result}")

                        self.wip_fab_bll.update_supplier_progress(result.to_dict(orient="records"))
                        continue

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