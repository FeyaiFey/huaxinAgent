import sys
import os
import logging
import time
from datetime import datetime
from typing import Dict, List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.email_client import EmailClient
from utils.logger import Logger
from utils.emailHelper import EmailHelper

# 设置日志
logger = Logger(__name__)

def test_email_system():

    """测试邮件系统"""
    try:
        # 1. 初始化邮件客户端
        logger.info("\n1. 初始化邮件客户端")
        start_time = time.time()
        email_client = EmailClient('config/email_config.yaml')
        
        init_time = time.time() - start_time
        logger.info(f"初始化耗时: {init_time:.4f}秒")
            
        # 2. 测试邮件服务器连接
        logger.info("\n2. 测试邮件服务器连接")
        start_time = time.time()
        email_client.connect()
        imap = email_client.imap
        email_helper = EmailHelper(imap)
        connect_time = time.time() - start_time
        logger.info(f"连接耗时: {connect_time:.4f}秒")
        

        try:
            # 3. 获取未读邮件
            logger.info("\n3. 获取未读邮件")
            start_time = time.time()
            emails = email_client.get_unread_emails()
            fetch_time = time.time() - start_time
            

            logger.info(f"获取完成，耗时: {fetch_time:.4f}秒")
            logger.info(f"发现 {len(emails)} 封未读邮件")

            # 4. 处理邮件
            logger.info("\n4. 处理邮件")
            

            # 统计信息
            stats = {
                'total': len(emails),
                'processed': 0,
                'matched': 0,
                'unmatched': 0,
                'error': 0,
                'start_time': time.time()
            }
            
            # 处理每封邮件
            for email_id in emails:
                try:
                    email_id = email_helper.normalize_email_id(email_id)
                    print(email_id)
                    msg = email_helper.fetch_email(email_id)
                    email_data = email_helper.parse_email_data(msg, email_id)
                    logger.info(f"\n处理邮件 {email_id}:")
                    
                    # 处理邮件
                    start_time = time.time()
                    result = email_client.process_email(email_id)
                    process_time = time.time() - start_time
                    

                    stats['processed'] += 1
                    if result:
                        stats['matched'] += 1
                        logger.info(f"处理成功，耗时: {process_time:.4f}秒")
                    else:
                        stats['unmatched'] += 1
                        logger.info("邮件不匹配任何规则，已跳过")
                        
                except Exception as e:
                    stats['error'] += 1
                    logger.error(f"处理邮件出错: {str(e)}")
                    continue
                    
            # 5. 输出统计信息
            logger.info("\n5. 处理统计")
            total_time = time.time() - stats['start_time']
            
            logger.info(f"总邮件数: {stats['total']}")
            logger.info(f"处理完成: {stats['processed']}")
            logger.info(f"规则匹配: {stats['matched']}")
            logger.info(f"规则未匹配: {stats['unmatched']}")
            logger.info(f"处理出错: {stats['error']}")
            
            if stats['processed'] > 0:
                logger.info(f"平均处理时间: {total_time/stats['processed']:.4f}秒/封")
            
            logger.info(f"总耗时: {total_time:.4f}秒")
            
        finally:
            # 6. 断开连接
            logger.info("\n6. 断开连接")
            email_client.disconnect()
            

        logger.info("\n测试完成!")
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)
        
if __name__ == "__main__":
    test_email_system()
