"""
日志工具模块
提供统一的日志记录和管理功能
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

class Logger:
    """日志记录器类"""
    
    _loggers = {}
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        """
        初始化日志记录器
        
        参数:
            name: 日志记录器名称
            config: 日志配置
        """
        # 处理日志记录器名称
        self.logger_name = name.split('.')[-1]  # 使用类名作为日志记录器名称
        
        if self.logger_name in self._loggers:
            self.logger = self._loggers[self.logger_name]
            return
            
        self.logger = logging.getLogger(self.logger_name)
        self._setup_logger(config or {})
        self._loggers[self.logger_name] = self.logger
        
    def _setup_logger(self, config: Dict):
        """配置日志记录器"""
        log_config = config.get('logging', {})
        
        # 设置日志级别
        level = getattr(logging, log_config.get('level', 'INFO'))
        self.logger.setLevel(level)
        
        if self.logger.handlers:
            return
            
        # 创建日志目录
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # 日志文件名
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = log_dir / f"huaxinAgent_{date_str}.log"
        
        # 创建文件处理器(支持日志轮转)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=log_config.get('max_size', 10*1024*1024),
            backupCount=log_config.get('backup_count', 5),
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # 日志格式
        formatter = logging.Formatter(
            log_config.get('format', 
                '[ %(asctime)s ] [ %(name)s ] [ %(levelname)s ] %(message)s'),
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """记录调试信息"""
        self.logger.debug(message)
    
    def info(self, message):
        """记录一般信息"""
        self.logger.info(message)
    
    def warning(self, message):
        """记录警告信息"""
        self.logger.warning(message)
    
    def error(self, message, **kwargs):
        """记录错误信息"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message):
        """记录严重错误信息"""
        self.logger.critical(message)
    
    def exception(self, message):
        """记录异常信息，包含堆栈跟踪"""
        self.logger.exception(message)

def setup_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志文件目录
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志目录
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 创建文件处理器
    log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger 