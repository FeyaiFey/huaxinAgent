import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.crawlers.base import BaseCrawler
from modules.crawlers.hjtc_crawler import HJTCCrawler
from modules.crawlers.xinf_crawler import XinfCrawler
from utils.logger import Logger
from utils.helpers import load_yaml

# 设置日志
logger = Logger(__name__)

def test_hjtc_crawler():
    """测试和舰科技爬虫"""
    try:
        # 1. 初始化爬虫
        logger.info("\n1. 初始化和舰科技爬虫")
        config = load_yaml("config/crawler_config.yaml")
        crawlers_config = config["crawler"]["crawlers"]
        hjtc_config = crawlers_config['hjtc']
        crawler = HJTCCrawler(hjtc_config)
        result = crawler.run()

        if not result:
            logger.error("和舰科技爬虫测试失败")
            raise Exception("和舰科技爬虫测试失败")
        logger.info("\n和舰科技爬虫测试完成!")
    except Exception as e:
        logger.error(f"和舰科技爬虫测试失败: {str(e)}")
        raise

def main():
    """运行所有测试"""
    try:
        # 测试基础爬虫
        
        # 测试和舰科技爬虫
        test_hjtc_crawler()
        
        logger.info("\n所有测试完成!")
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()
