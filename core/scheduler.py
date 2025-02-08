"""
调度器模块
负责协调和调度各个功能模块的运行
"""

from datetime import datetime
import threading
from typing import Dict, Any
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from utils.logger import Logger
from utils.helpers import load_yaml
from .email_processor import EmailProcessor
from .crawler_processor import CrawlerProcessor

class Scheduler:
    """调度器类"""
    
    def __init__(self):
        """初始化调度器"""
        self.logger = Logger(__name__)
        self.config = load_yaml('config/settings.yaml')
        self.crawler_config = load_yaml('config/crawler_config.yaml')
        self.scheduler = BackgroundScheduler()
        self.crawler_processor = CrawlerProcessor()
        self.email_processor = None  # 初始化时不创建EmailProcessor实例
        self._setup_jobs()
        
    def _setup_jobs(self):
        """设置定时任务"""
        # 获取功能开关配置
        email_config = self.config['features']['email_processor']
        crawler_enabled = self.config['features']['crawler']['enabled']
            
        # 设置爬虫任务
        if crawler_enabled and self.crawler_config['crawler']['enabled']:
            # 如果配置了启动时执行，则先执行一次爬虫任务
            if self.crawler_config['crawler']['schedule'].get('run_on_start', True):
                self.logger.debug("系统启动，执行首次爬虫任务...")
                self._run_crawler_processor()
            
            # 解析时间
            hour, minute = self.crawler_config['crawler']['schedule']['run_time'].split(':')
            # 设置定时任务
            self.scheduler.add_job(
                func=self._run_crawler_processor,
                trigger=CronTrigger(
                    hour=int(hour),
                    minute=int(minute)
                ),
                id='crawler_processor',
                name='爬虫任务',
                replace_existing=True
            )
            self.logger.debug(
                f"爬虫任务已设置，执行时间：{self.crawler_config['crawler']['schedule']['run_time']}"
            )
        else:
            self.logger.info("爬虫功能已禁用")
        
        # 设置邮件处理任务
        if email_config['enabled']:
            # 如果配置了启动时执行，则先执行一次邮件处理任务
            if email_config.get('run_on_start', True):
                self.logger.debug("系统启动，执行首次邮件处理任务...")
                self._run_email_processor()
            
            # 设置定时任务
            self.scheduler.add_job(
                func=self._run_email_processor,
                trigger=IntervalTrigger(
                    seconds=email_config['check_interval']
                ),
                id='email_processor',
                name='邮件处理任务',
                replace_existing=True
            )
            self.logger.debug(
                f"邮件处理任务已设置，间隔：{email_config['check_interval']}秒"
            )
            
    def _run_email_processor(self):
        """运行邮件处理器"""
        try:
            self.logger.info("开始执行邮件处理任务...")
            # 每次运行时创建新的EmailProcessor实例
            self.email_processor = EmailProcessor()
            stats = self.email_processor.process_unread_emails()
            self.logger.debug(f"邮件处理任务完成: {stats}")
            
        except Exception as e:
            self.logger.error(f"邮件处理任务失败: {str(e)}", exc_info=True)
        finally:
            # 任务完成后清理资源
            if self.email_processor:
                self.email_processor = None
            
    def _run_crawler_processor(self):
        """运行爬虫处理器"""
        try:
            self.logger.info("开始执行爬虫任务...")
            stats = self.crawler_processor.run_all_crawlers()
            
            # 检查爬虫执行结果
            if stats['failed'] > 0:
                self.logger.error(
                    f"爬虫任务完成但有失败: {stats}\n"
                    f"失败详情: {', '.join(name for name, result in stats['results'].items() if result['status'] == 'failed')}"
                )
            else:
                self.logger.debug(f"爬虫任务成功完成: {stats}")
            
        except Exception as e:
            self.logger.error(f"爬虫任务失败: {str(e)}", exc_info=True)
            
    def start(self):
        """启动调度器"""
        try:
            self.scheduler.start()
            self.logger.debug("调度器已启动")
            
        except Exception as e:
            self.logger.error(f"启动调度器失败: {str(e)}", exc_info=True)
            raise
            
    def stop(self):
        """停止调度器"""
        try:
            self.scheduler.shutdown()
            self.logger.debug("调度器已停止")
            
        except Exception as e:
            self.logger.error(f"停止调度器失败: {str(e)}", exc_info=True)
            
    def get_jobs_status(self) -> Dict[str, Any]:
        """
        获取所有任务的状态
        Returns:
            任务状态信息
        """
        jobs_status = {}
        for job in self.scheduler.get_jobs():
            jobs_status[job.id] = {
                'name': job.name,
                'next_run_time': job.next_run_time,
                'pending': job.pending
            }
        return jobs_status
