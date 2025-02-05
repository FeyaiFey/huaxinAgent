import sys
import os
import logging
from datetime import date, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.database import DatabaseSession
from dal.wip_fab import WipFabDAL

# 设置基本的日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_wip_fab_dal():
    """测试WIP FAB数据访问层"""
    try:
        dal = WipFabDAL()
        
        with DatabaseSession() as session:
            # 1. 测试获取所有记录
            all_records = dal.get_all(session)
            logger.info(f"\n1. 总共找到 {len(all_records)} 条记录")
            
            if all_records:
                first_record = all_records[0]
                lot = first_record.lot
                purchase_order = first_record.purchaseOrder
                status = first_record.status
                
                # 2. 测试通过批次号获取
                record = dal.get_by_lot(session, lot)
                logger.info(f"\n2. 通过批次号 {lot} 获取记录:")
                logger.info(f"找到记录: {record}")
                
                # 3. 测试通过采购订单获取
                if purchase_order:
                    records = dal.get_by_purchase_order(session, purchase_order)
                    logger.info(f"\n3. 通过采购订单 {purchase_order} 获取记录:")
                    logger.info(f"找到 {len(records)} 条记录")
                
                # 4. 测试通过状态获取
                if status:
                    records = dal.get_by_status(session, status)
                    logger.info(f"\n4. 通过状态 {status} 获取记录:")
                    logger.info(f"找到 {len(records)} 条记录")
                
                # 5. 测试获取未完成记录
                incomplete_records = dal.get_incomplete(session)
                logger.info(f"\n5. 未完成记录:")
                logger.info(f"找到 {len(incomplete_records)} 条记录")
                
                # 6. 测试日期范围查询
                today = date.today()
                start_date = today - timedelta(days=30)
                end_date = today + timedelta(days=30)
                date_range_records = dal.get_by_forecast_date_range(session, start_date, end_date)
                logger.info(f"\n6. {start_date} 到 {end_date} 的记录:")
                logger.info(f"找到 {len(date_range_records)} 条记录")
                
                # 7. 测试完成率范围查询
                rate_range_records = dal.get_by_completion_rate_range(session, 50, 100)
                logger.info(f"\n7. 完成率在 50%-100% 之间的记录:")
                logger.info(f"找到 {len(rate_range_records)} 条记录")
                
                # 8. 测试状态更新
                if record:
                    original_status = record.status
                    updated_record = dal.update_status(session, lot, "测试状态")
                    logger.info(f"\n8. 状态更新测试:")
                    logger.info(f"原状态: {original_status}")
                    logger.info(f"新状态: {updated_record.status if updated_record else '更新失败'}")
                    # 恢复原状态
                    dal.update_status(session, lot, original_status)
                
                # 9. 测试进度更新
                if record and record.remainLayer is not None:
                    original_remain = record.remainLayer
                    updated_record = dal.update_progress(session, lot, original_remain + 1)
                    logger.info(f"\n9. 进度更新测试:")
                    logger.info(f"原剩余层数: {original_remain}")
                    logger.info(f"新剩余层数: {updated_record.remainLayer if updated_record else '更新失败'}")
                    # 恢复原值
                    dal.update_progress(session, lot, original_remain)
            
            logger.info("\n测试完成!")
            
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_wip_fab_dal() 