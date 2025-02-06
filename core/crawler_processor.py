"""
爬虫处理核心模块
负责协调和执行所有爬虫任务
"""

import importlib
import pkgutil
from typing import List, Dict, Any, Type
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.logger import Logger
from modules.crawlers.base import BaseCrawler
import modules.crawlers as crawler_package
from utils.helpers import load_yaml

class CrawlerProcessor:
    """爬虫处理器核心类"""
    
    def __init__(self):
        """初始化爬虫处理器"""
        self.logger = Logger(__name__)
        self.settings = load_yaml('config/settings.yaml')
        self.crawler_config = load_yaml('config/crawler_config.yaml')
        self.crawlers: List[BaseCrawler] = []
        self._load_crawlers()
        
    def _load_crawlers(self) -> None:
        """动态加载所有爬虫类"""
        try:
            # 获取爬虫包中的所有模块
            crawler_modules = [
                name for _, name, _ in pkgutil.iter_modules(crawler_package.__path__)
                if not name.startswith('_') and name != 'base'
            ]
            
            # 获取爬虫配置
            crawlers_config = self.crawler_config["crawler"]["crawlers"]
            
            # 动态导入每个爬虫模块
            for module_name in crawler_modules:
                try:
                    module = importlib.import_module(f"modules.crawlers.{module_name}")
                    # 查找模块中的爬虫类（继承自BaseCrawler的类）
                    crawler_classes = [
                        cls for name, cls in module.__dict__.items()
                        if isinstance(cls, type) 
                        and issubclass(cls, BaseCrawler) 
                        and cls != BaseCrawler
                    ]
                    
                    # 实例化找到的爬虫类
                    for crawler_class in crawler_classes:
                        # 根据类名获取对应配置
                        crawler_name = crawler_class.__name__.lower().replace('crawler', '')
                        if crawler_name in crawlers_config and crawlers_config[crawler_name].get('enabled', True):
                            # 创建完整的配置字典
                            config = {
                                'username': crawlers_config[crawler_name].get('username'),
                                'password': crawlers_config[crawler_name].get('password'),
                                'output_dir': crawlers_config[crawler_name].get('output_dir'),
                                'remember_me': crawlers_config[crawler_name].get('remember_me', True),
                                'enabled': crawlers_config[crawler_name].get('enabled', True)
                            }
                            # 实例化爬虫
                            crawler_instance = crawler_class(config=config)
                            self.crawlers.append(crawler_instance)
                            self.logger.debug(f"加载爬虫: {crawler_class.__name__}")
                        else:
                            self.logger.warning(f"未找到爬虫 {crawler_class.__name__} 的配置信息或爬虫已禁用")
                        
                except Exception as e:
                    self.logger.error(f"加载爬虫模块 {module_name} 失败: {str(e)}", exc_info=True)
                    
        except Exception as e:
            self.logger.error(f"加载爬虫失败: {str(e)}", exc_info=True)
            raise
            
    def run_all_crawlers(self, max_workers: int = 3) -> Dict[str, Any]:
        """
        并行运行所有爬虫
        Args:
            max_workers: 最大并行工作线程数
        Returns:
            运行统计信息
        """
        stats = {
            'total': len(self.crawlers),
            'successful': 0,
            'failed': 0,
            'results': {}
        }
        
        try:
            # 使用线程池并行执行爬虫
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有爬虫任务
                future_to_crawler = {
                    executor.submit(crawler.run): crawler
                    for crawler in self.crawlers
                }
                
                # 处理完成的任务
                for future in as_completed(future_to_crawler):
                    crawler = future_to_crawler[future]
                    try:
                        result = future.result()
                        # 检查爬虫执行结果
                        if result is False:  # 如果爬虫返回False表示执行失败
                            stats['failed'] += 1
                            stats['results'][crawler.__class__.__name__] = {
                                'status': 'failed',
                                'error': '爬虫执行失败'
                            }
                            self.logger.error(f"爬虫 {crawler.__class__.__name__} 执行失败")
                        else:
                            stats['successful'] += 1
                            stats['results'][crawler.__class__.__name__] = {
                                'status': 'success',
                                'data': result
                            }
                            self.logger.debug(f"爬虫 {crawler.__class__.__name__} 执行成功")
                        
                    except Exception as e:
                        stats['failed'] += 1
                        stats['results'][crawler.__class__.__name__] = {
                            'status': 'failed',
                            'error': str(e)
                        }
                        self.logger.error(
                            f"爬虫 {crawler.__class__.__name__} 执行失败: {str(e)}", 
                            exc_info=True
                        )
            
            self.logger.info(
                f"爬虫任务完成: 总数 {stats['total']}, "
                f"成功 {stats['successful']}, "
                f"失败 {stats['failed']}"
            )
            return stats
            
        except Exception as e:
            self.logger.error(f"执行爬虫任务时发生错误: {str(e)}", exc_info=True)
            raise
            
    def run_specific_crawlers(self, crawler_names: List[str], max_workers: int = 3) -> Dict[str, Any]:
        """
        运行指定的爬虫
        Args:
            crawler_names: 要运行的爬虫类名列表
            max_workers: 最大并行工作线程数
        Returns:
            运行统计信息
        """
        # 筛选指定的爬虫
        selected_crawlers = [
            crawler for crawler in self.crawlers
            if crawler.__class__.__name__ in crawler_names
        ]
        
        if not selected_crawlers:
            self.logger.warning(f"未找到指定的爬虫: {crawler_names}")
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'results': {}
            }
            
        # 保存原始爬虫列表
        original_crawlers = self.crawlers
        self.crawlers = selected_crawlers
        
        try:
            # 运行选定的爬虫
            stats = self.run_all_crawlers(max_workers)
            return stats
            
        finally:
            # 恢复原始爬虫列表
            self.crawlers = original_crawlers 