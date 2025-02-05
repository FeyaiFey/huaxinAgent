import sys
import os
import logging
from datetime import date

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.database import DatabaseSession
from models.wip_fab import WipFab

# 设置基本的日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_wip_fab_model():
    """测试WIP FAB模型"""
    try:
        with DatabaseSession() as session:
            # 查询所有记录
            wip_fabs = session.query(WipFab).all()
            
            logger.info(f"总共找到 {len(wip_fabs)} 条记录")
            
            # 显示第一条记录的详细信息
            if wip_fabs:
                first_wip = wip_fabs[0]
                logger.info("\n第一条记录的详细信息:")
                logger.info(f"批次号: {first_wip.lot}")
                logger.info(f"产品名称: {first_wip.itemName}")
                logger.info(f"采购订单: {first_wip.purchaseOrder}")
                logger.info(f"数量: {first_wip.qty}")
                logger.info(f"状态: {first_wip.status}")
                logger.info(f"阶段: {first_wip.stage}")
                logger.info(f"总层数: {first_wip.layerCount}")
                logger.info(f"剩余层数: {first_wip.remainLayer}")
                logger.info(f"当前位置: {first_wip.currentPisition}")
                logger.info(f"预计完成日期: {first_wip.forecastDate}")
                logger.info(f"完成率: {first_wip.completion_rate}%")
                logger.info(f"是否完成: {first_wip.is_completed}")
                logger.info(f"创建时间: {first_wip.create_at}")
                logger.info(f"修改时间: {first_wip.modified_at}")
                
                # 测试to_dict方法
                logger.info("\n转换为字典格式:")
                logger.info(first_wip.to_dict())
            
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_wip_fab_model() 