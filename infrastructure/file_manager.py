"""
文件系统管理模块
提供文件操作的统一接口，包括文件的创建、删除、移动、临时文件管理等功能
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Union
from utils.logger import Logger

class FileManager:
    """文件系统管理类"""
    
    def __init__(self, base_dir: str = None):
        """
        初始化文件管理器
        Args:
            base_dir: 基础目录，默认为项目根目录
        """
        self.logger = Logger(__name__)
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.temp_dir = self.base_dir / 'temp'
        self.attachment_dir = self.base_dir / 'attachments'
        
        # 创建必要的目录
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.temp_dir,
            self.attachment_dir,
            self.attachment_dir / 'temp',
            self.attachment_dir / 'temp' / '进度表',
            self.attachment_dir / 'temp' / '送货单',
            self.attachment_dir / 'temp' / '测试报告',
            self.attachment_dir / 'archived'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_attachment(self, file_data: bytes, filename: str, category: str) -> Path:
        """
        保存附件文件
        Args:
            file_data: 文件数据
            filename: 文件名
            category: 文件分类（进度表/送货单/测试报告）
        Returns:
            保存后的文件路径
        """
        try:
            # 构建保存路径
            save_dir = self.attachment_dir / 'temp' / category
            save_path = save_dir / filename
            
            # 写入文件
            with open(save_path, 'wb') as f:
                f.write(file_data)
            
            self.logger.info(f"附件保存成功: {save_path}")
            return save_path
            
        except Exception as e:
            self.logger.error(f"保存附件失败: {str(e)}", exc_info=True)
            raise
    
    def create_temp_file(self, prefix: str = '', suffix: str = '') -> Path:
        """
        创建临时文件
        Args:
            prefix: 文件名前缀
            suffix: 文件扩展名
        Returns:
            临时文件路径
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{prefix}_{timestamp}{suffix}" if prefix else f"temp_{timestamp}{suffix}"
            temp_path = self.temp_dir / filename
            
            # 创建空文件
            temp_path.touch()
            
            return temp_path
            
        except Exception as e:
            self.logger.error(f"创建临时文件失败: {str(e)}", exc_info=True)
            raise
    
    def archive_file(self, file_path: Union[str, Path], category: str) -> Optional[Path]:
        """
        归档文件
        Args:
            file_path: 源文件路径
            category: 文件分类
        Returns:
            归档后的文件路径
        """
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                self.logger.warning(f"要归档的文件不存在: {source_path}")
                return None
            
            # 构建归档路径
            archive_dir = self.attachment_dir / 'archived' / category / datetime.now().strftime('%Y%m')
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # 移动文件到归档目录
            archive_path = archive_dir / source_path.name
            shutil.move(str(source_path), str(archive_path))
            
            self.logger.info(f"文件归档成功: {archive_path}")
            return archive_path
            
        except Exception as e:
            self.logger.error(f"文件归档失败: {str(e)}", exc_info=True)
            raise
    
    def clean_temp_files(self, days: int = 7):
        """
        清理指定天数之前的临时文件
        Args:
            days: 保留的天数
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 清理临时目录
            for file_path in self.temp_dir.glob('*'):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_date:
                        file_path.unlink()
                        self.logger.info(f"清理临时文件: {file_path}")
            
            # 清理临时附件目录
            temp_attachment_dir = self.attachment_dir / 'temp'
            for category_dir in temp_attachment_dir.glob('*'):
                if category_dir.is_dir():
                    for file_path in category_dir.glob('*'):
                        if file_path.is_file():
                            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                            if file_time < cutoff_date:
                                file_path.unlink()
                                self.logger.info(f"清理临时附件: {file_path}")
                                
        except Exception as e:
            self.logger.error(f"清理临时文件失败: {str(e)}", exc_info=True)
            raise
    
    def get_files_by_pattern(self, directory: Union[str, Path], pattern: str) -> List[Path]:
        """
        根据模式获取文件列表
        Args:
            directory: 目录路径
            pattern: 文件匹配模式（例如：*.xlsx）
        Returns:
            匹配的文件路径列表
        """
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                self.logger.warning(f"目录不存在: {dir_path}")
                return []
            
            return list(dir_path.glob(pattern))
            
        except Exception as e:
            self.logger.error(f"获取文件列表失败: {str(e)}", exc_info=True)
            raise
    
    def ensure_directory(self, directory: Union[str, Path]) -> Path:
        """
        确保目录存在，如果不存在则创建
        Args:
            directory: 目录路径
        Returns:
            目录路径对象
        """
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
