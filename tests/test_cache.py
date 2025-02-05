import sys
import os
import logging
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bll.wip_fab import WipFabBLL
from utils.cache import TimedCache

# 设置基本的日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_speedup(time1: float, time2: float) -> str:
    """计算加速比"""
    if time2 < 0.0001:  # 避免除零
        return "∞"  # 无限大
    return f"{time1/time2:.2f}"

def test_cache():
    """测试缓存机制"""
    try:
        bll = WipFabBLL()
        
        # 1. 测试WIP汇总信息缓存
        logger.info("\n1. 测试WIP汇总信息缓存")
        
        # 第一次调用（缓存未命中）
        start_time = time.time()
        summary1 = bll.get_wip_summary()
        time1 = time.time() - start_time
        logger.info(f"首次调用耗时: {time1:.4f}秒")
        logger.info(f"- 总数量：{summary1['total_count']}")
        logger.info(f"- 在制数量：{summary1['in_progress_count']}")
        
        # 第二次调用（应该命中缓存）
        start_time = time.time()
        summary2 = bll.get_wip_summary()
        time2 = time.time() - start_time
        logger.info(f"第二次调用耗时: {time2:.4f}秒")
        logger.info(f"缓存加速比: {calculate_speedup(time1, time2)}倍")
        
        # 2. 测试延期项目缓存
        logger.info("\n2. 测试延期项目缓存")
        
        # 第一次调用
        start_time = time.time()
        delayed1 = bll.get_delayed_items()
        time1 = time.time() - start_time
        logger.info(f"首次调用耗时: {time1:.4f}秒")
        logger.info(f"延期项目数量: {len(delayed1)}")
        
        # 第二次调用（应该命中缓存）
        start_time = time.time()
        delayed2 = bll.get_delayed_items()
        time2 = time.time() - start_time
        logger.info(f"第二次调用耗时: {time2:.4f}秒")
        logger.info(f"缓存加速比: {calculate_speedup(time1, time2)}倍")
        
        # 3. 测试缓存清除
        logger.info("\n3. 测试缓存清除")
        
        # 更新数据（应该清除缓存）
        supplier_data = [{
            'lot': 'TEST001',
            'purchaseOrder': 'PO001',
            'itemName': '测试产品1',
            'qty': 100,
            'status': '在制',
            'stage': '压合',
            'layerCount': 10,
            'remainLayer': 5,
            'currentPisition': '压合站',
            'forecastDate': datetime.now().strftime('%Y-%m-%d')
        }]
        
        stats = bll.update_supplier_progress(supplier_data)
        logger.info("数据更新完成:")
        logger.info(f"- 新增: {stats['inserted']}条")
        logger.info(f"- 更新: {stats['updated']}条")
        logger.info(f"- 完成: {stats['completed']}条")
        
        # 再次调用（应该重新查询）
        start_time = time.time()
        summary3 = bll.get_wip_summary()
        time3 = time.time() - start_time
        logger.info(f"缓存清除后调用耗时: {time3:.4f}秒")
        logger.info(f"与缓存命中比较: {calculate_speedup(time3, time2)}倍")
        
        # 4. 测试缓存状态
        logger.info("\n4. 测试缓存状态")
        cache_info = bll.get_cache_info()
        for cache_name, info in cache_info.items():
            logger.info(f"{cache_name}:")
            logger.info(f"- 总项数: {info['total_items']}")
            logger.info(f"- 活跃项数: {info['active_items']}")
            logger.info(f"- 过期项数: {info['expired_items']}")
        
        # 5. 测试自定义缓存装饰器
        logger.info("\n5. 测试自定义缓存装饰器")
        
        # 创建测试缓存（1秒过期）
        test_cache = TimedCache(seconds=1)
        
        @test_cache
        def cached_function(x: int) -> int:
            logger.info("执行函数计算")
            time.sleep(0.1)  # 模拟耗时操作
            return x * x
        
        # 第一次调用
        logger.info("首次调用")
        start_time = time.time()
        result1 = cached_function(5)
        time1 = time.time() - start_time
        logger.info(f"耗时: {time1:.4f}秒")
        logger.info(f"结果: {result1}")
        
        # 立即再次调用（应该命中缓存）
        logger.info("\n立即再次调用")
        start_time = time.time()
        result2 = cached_function(5)
        time2 = time.time() - start_time
        logger.info(f"耗时: {time2:.4f}秒")
        logger.info(f"结果: {result2}")
        logger.info(f"缓存加速比: {calculate_speedup(time1, time2)}倍")
        
        # 等待缓存过期
        logger.info("\n等待1秒让缓存过期...")
        time.sleep(1.1)
        
        # 再次调用（应该重新计算）
        logger.info("缓存过期后调用")
        start_time = time.time()
        result3 = cached_function(5)
        time3 = time.time() - start_time
        logger.info(f"耗时: {time3:.4f}秒")
        logger.info(f"结果: {result3}")
        
        # 6. 测试不同参数的缓存
        logger.info("\n6. 测试不同参数的缓存")
        
        # 使用不同参数调用
        logger.info("使用不同参数调用")
        result4 = cached_function(10)  # 应该重新计算
        logger.info(f"参数10的结果: {result4}")
        
        # 再次使用原参数调用
        logger.info("\n再次使用原参数调用")
        result5 = cached_function(5)  # 应该重新计算（因为之前已过期）
        logger.info(f"参数5的结果: {result5}")
        
        logger.info("\n测试完成!")
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_cache() 