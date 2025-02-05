import sys
import os
import logging
from datetime import date, datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.database import DatabaseSession
from dal.wip_fab import WipFabDAL

# 设置基本的日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_supplier_update():
    """测试供应商数据更新"""
    try:
        dal = WipFabDAL()
        
        # 模拟供应商数据
        supplier_data = [
            {
                'lot': 'TEST001',
                'purchaseOrder': 'PO001',
                'itemName': '测试产品1',
                'qty': 100,
                'status': '在制',
                'stage': '压合',
                'layerCount': 10,
                'remainLayer': 5,
                'currentPisition': '压合站',
                'forecastDate': date.today() + timedelta(days=7)
            },
            {
                'lot': 'TEST002',
                'purchaseOrder': 'PO001',
                'itemName': '测试产品2',
                'qty': 200,
                'status': '在制',
                'stage': '钻孔',
                'layerCount': 8,
                'remainLayer': 3,
                'currentPisition': '钻孔站',
                'forecastDate': date.today() + timedelta(days=5)
            }
        ]
        
        with DatabaseSession() as session:
            # 执行批量更新
            logger.info("开始更新供应商数据...")
            stats = dal.batch_update_supplier_data(session, supplier_data)
            
            # 输出更新统计
            logger.info("更新完成！统计信息：")
            logger.info(f"- 新增记录：{stats['inserted']}条")
            logger.info(f"- 更新记录：{stats['updated']}条")
            logger.info(f"- 完成记录：{stats['completed']}条")
            
            # 验证更新结果
            logger.info("\n验证更新后的记录：")
            for lot in ['TEST001', 'TEST002']:
                record = dal.get_by_lot(session, lot)
                if record:
                    logger.info(f"\n批次号 {lot} 的记录：")
                    logger.info(f"- 状态：{record.status}")
                    logger.info(f"- 阶段：{record.stage}")
                    logger.info(f"- 剩余层数：{record.remainLayer}")
                    logger.info(f"- 完成率：{record.completion_rate}%")
                    logger.info(f"- 预计完成日期：{record.forecastDate}")
                    logger.info(f"- 完工日期：{record.finished_at}")
            
            # 验证已完成的记录
            completed_records = dal.get_by_status(session, "已完结")
            logger.info(f"\n已完结记录数：{len(completed_records)}")
            
            # 回滚测试数据
            session.rollback()
            logger.info("\n测试完成，数据已回滚！")
            
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_supplier_update() 