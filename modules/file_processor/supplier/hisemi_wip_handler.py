import pandas as pd
import datetime
from typing import Dict, List, Optional, Any

from .base_delivery_handler import BaseDeliveryExcelHandler
from utils.helpers import load_yaml
from utils.logger import Logger

class HisemiWipHandler(BaseDeliveryExcelHandler):
    """
    上华FAB2Excel处理器
    """
    def __init__(self):
        fields_config = load_yaml("config/wip_fields.yaml")
        self.config = fields_config["wip_fields"]["封装厂"]["池州华宇"]
        self.craft_forecast = fields_config["wip_fields"]["craft_forecast"]
        self.logger = Logger(__name__)

    def process(self, match_result: Dict[str, Any]) -> pd.DataFrame:
        """
        处理池州华宇wip的Excel文件

        Args:
            match_result: 规则引擎匹配结果
            枚举:
             match_result:{
                'actions': {'save_attachment': True, 'mark_as_read': True, 'attachment_folder': 'attachments/temp/封装送货单/池州华宇'},
                'name': '封装送货单-池州华宇',
                'category': '封装送货单',
                'supplier': '池州华宇',
                'attachments': ['attachments/temp/封装厂/池州华宇/1.pdf', 'attachments/temp/封装厂/池州华宇/2.pdf']
            }
            
        Returns:
            pd.DataFrame: 处理结果
        """
        try:
            key_columns = self.config["关键字段映射"]
            data_format = self.craft_forecast.keys()
            names = list(key_columns.keys())
            attachments = match_result.get("attachments")
            if not attachments:
                self.logger.error(f"匹配结果中缺少附件")
                return None
            
            # 读取Excel文件
            try:
                df = pd.read_excel(attachments[0], header=0, sheet_name="Sheet1")
                
                # 检查DataFrame是否为空
                if df.empty:
                    self.logger.error("Excel文件内容为空")
                    return None
                    
                # 检查是否包含所需的列
                missing_columns = set(names) - set(df.columns)
                if missing_columns:
                    self.logger.error(f"Excel文件缺少必要的列: {missing_columns}")
                    return None
                    
            except ValueError as e:
                if "No sheet named" in str(e):
                    self.logger.error("Excel文件中没有名为'wip'的工作表")
                    return None
                raise

            df = df[names]
            # 创建映射字典
            mapping_dict = {k: v for k, v in key_columns.items()}
            # 重命名列
            df.rename(columns=mapping_dict, inplace=True)

            df = df[data_format]






        
        except Exception as e:
            self.logger.error(f"处理Excel文件时发生错误: {e}")
            return None
        
    
