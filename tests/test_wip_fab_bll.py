import sys
import os
import logging
from datetime import date, datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bll.wip_fab import WipFabBLL

# 设置基本的日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_wip_fab_bll():
    """测试WIP FAB业务逻辑层"""
    try:
        bll = WipFabBLL()
        
        # 1. 测试数据更新
        logger.info("\n1. 测试供应商数据更新")
        supplier_data = [
            {
                'lot': 'TEST001',
                'purchaseOrder': 'PO001',
                'itemName': '测试产品1',
                'qty': '100',  # 故意使用字符串测试类型转换
                'status': '在制',
                'stage': '压合',
                'layerCount': '10',  # 故意使用字符串测试类型转换
                'remainLayer': '5',   # 故意使用字符串测试类型转换
                'currentPisition': '压合站',
                'forecastDate': date.today().strftime('%Y-%m-%d')  # 测试日期字符串转换
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
                'forecastDate': (date.today() + timedelta(days=5)).strftime('%Y-%m-%d')
            },
            # 添加一个无效数据测试验证
            {
                'lot': 'TEST003',
                'layerCount': 5,
                'remainLayer': 10  # 故意设置剩余层数大于总层数
            }
        ]
        
        stats = bll.update_supplier_progress(supplier_data)
        logger.info("更新统计:")
        logger.info(f"- 新增记录：{stats['inserted']}条")
        logger.info(f"- 更新记录：{stats['updated']}条")
        logger.info(f"- 完成记录：{stats['completed']}条")
        
        # 2. 测试WIP汇总信息
        logger.info("\n2. 测试WIP汇总信息")
        summary = bll.get_wip_summary()
        logger.info("WIP汇总:")
        logger.info(f"- 总数量：{summary['total_count']}")
        logger.info(f"- 在制数量：{summary['in_progress_count']}")
        logger.info(f"- 完成数量：{summary['completed_count']}")
        logger.info(f"- 平均完成率：{summary['avg_completion_rate']}%")
        logger.info(f"- 统计时间：{summary['statistics_time']}")
        
        # 3. 测试延期项目查询
        logger.info("\n3. 测试延期项目查询")
        delayed_items = bll.get_delayed_items(days_threshold=0)  # 使用0天便于测试
        logger.info(f"延期项目数量：{len(delayed_items)}")
        for item in delayed_items[:5]:  # 只显示前5个
            logger.info(f"- {item.lot}: {item.forecastDate}")
        
        # 4. 测试完成预测
        logger.info("\n4. 测试完成预测")
        forecast = bll.get_completion_forecast(days=30)
        logger.info("未来30天完成预测:")
        for date_key, count in sorted(forecast.items()):
            logger.info(f"- {date_key}: {count}个")
        
        logger.info("\n测试完成!")
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_wip_fab_bll() 