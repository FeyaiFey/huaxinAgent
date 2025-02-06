"""
供应商Excel处理器基类
定义供应商Excel处理的基本接口
"""

from typing import Dict, Optional, Any
from abc import ABC, abstractmethod
from .utils import SupplierUtils
from utils.logger import Logger

class BaseDeliveryExcelHandler(ABC):
    """供应商Excel处理器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化处理器
        
        Args:
            config: 送货单输出格式配置：config\delivery_json_format.yaml
        """
        self.logger = Logger(__name__)
        self.config = config
        self.utils = SupplierUtils(config)
    
    @abstractmethod
    def process(self, match_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        处理Excel文件
        
        Args:
            match_result: 规则引擎匹配结果
            
        Returns:
            Dict: 处理结果
        """
        pass 