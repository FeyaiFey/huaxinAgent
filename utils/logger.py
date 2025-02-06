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
from utils.helpers import load_yaml

class Logger:
    """日志记录器类"""
    
    _loggers = {}
    _config = None
    
    @classmethod
    def _load_config(cls):
        """加载日志配置"""
        if cls._config is None:
            try:
                # 首先尝试加载专门的日志配置
                cls._config = load_yaml('config/logging.yaml')
            except Exception:
                try:
                    # 如果不存在，则从全局配置加载
                    cls._config = load_yaml('config/settings.yaml')
                except Exception:
                    cls._config = {}
    
    def __init__(self, name: str):
        """
        初始化日志记录器
        
        参数:
            name: 日志记录器名称
        """
        # 加载配置
        self._load_config()
        
        # 处理日志记录器名称
        self.logger_name = name.split('.')[-1]  # 使用类名作为日志记录器名称
        
        if self.logger_name in self._loggers:
            self.logger = self._loggers[self.logger_name]
            return
            
        self.logger = logging.getLogger(self.logger_name)
        self._setup_logger()
        self._loggers[self.logger_name] = self.logger
        
    def _setup_logger(self):
        """配置日志记录器"""
        log_config = self._config.get('logging', {})
        
        # 获取模块特定配置
        logger_config = log_config.get('loggers', {}).get(self.logger_name, {})
        
        # 设置日志级别（优先使用模块特定配置）
        level = getattr(logging, logger_config.get('level', log_config.get('level', 'INFO')))
        self.logger.setLevel(level)
        
        if self.logger.handlers:
            return
            
        # 创建日志目录
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # 日志文件名
        date_str = datetime.now().strftime('%Y%m%d')
        filename_template = log_config.get('file', {}).get('filename_template', 'huaxinAgent_%Y%m%d.log')
        log_file = log_dir / datetime.now().strftime(filename_template)
        
        # 文件处理器配置
        file_config = log_config.get('file', {})
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=file_config.get('max_size', 10*1024*1024),
            backupCount=file_config.get('backup_count', 30),
            encoding='utf-8'
        )
        file_level = getattr(logging, file_config.get('level', 'DEBUG'))
        file_handler.setLevel(file_level)
        
        # 控制台处理器配置
        console_config = log_config.get('console', {})
        console_handler = logging.StreamHandler()
        console_level = getattr(logging, console_config.get('level', 'INFO'))
        console_handler.setLevel(console_level)
        
        # 日志格式
        formatter = logging.Formatter(
            log_config.get('format', 
                '[ %(asctime)s ] [ %(name)s ] [ %(levelname)s ] %(message)s'),
            datefmt=log_config.get('datefmt', '%Y-%m-%d %H:%M:%S')
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