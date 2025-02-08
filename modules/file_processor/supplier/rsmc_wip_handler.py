import pandas as pd
from typing import Dict, List, Optional, Any

from .base_delivery_handler import BaseDeliveryExcelHandler
from utils.helpers import load_yaml
from utils.logger import Logger


class RsmcHandler(BaseDeliveryExcelHandler):
    """
    荣芯Excel处理器
    """
    def __init__(self):
        self.logger = Logger(__name__)
        fields_config = load_yaml("config/wip_fields.yaml")
        self.config = fields_config["wip_fields"]["晶圆厂"]["荣芯"]
        self.data_format = fields_config["wip_fields"]["data_format"]

    def process(self, match_result: Dict[str, Any]) -> pd.DataFrame:
        """
        处理荣芯的Excel文件

        Args:
            match_result: 规则引擎匹配结果
            枚举:
             match_result:{
                'actions': {'save_attachment': True, 'mark_as_read': True, 'attachment_folder': 'attachments/temp/封装送货单/池州华宇'},
                'name': '封装送货单-池州华宇',
                'category': '封装送货单',
                'supplier': '池州华宇',
                'attachments': ['attachments/temp/晶圆厂/荣芯/1.pdf', 'attachments/temp/晶圆厂/荣芯/2.pdf']
            }
            
        Returns:
            pd.DataFrame: 处理结果
        """
        try:
            header = self.config["header"]
            names = self.config["names"]
            name_values = list(names.values())
            data_format = self.data_format
            attachments = match_result.get("attachments")
            if not attachments:
                self.logger.error(f"匹配结果中缺少附件")
                return None
            
            # 读取Excel文件
            try:
                df = pd.read_excel(attachments[0], header=header, sheet_name="WIP Report")
                
                # 检查DataFrame是否为空
                if df.empty:
                    self.logger.error("Excel文件内容为空")
                    return None
                    
                # 检查是否包含所需的列
                missing_columns = set(name_values) - set(df.columns)
                if missing_columns:
                    self.logger.error(f"Excel文件缺少必要的列: {missing_columns}")
                    return None
                    
            except ValueError as e:
                if "No sheet named" in str(e):
                    self.logger.error("Excel文件中没有名为'WIP Report'的工作表")
                    return None
                raise
            
            df = df[name_values]
            # 创建反向映射字典
            reverse_names = {v: k for k, v in names.items()}
            # 重命名列
            df.rename(columns=reverse_names, inplace=True)

            df["supplier"] = "荣芯"
            df["finished_at"] = pd.NaT

            # 处理数值型字段，将非数值转换为NaN
            df["remainLayer"] = pd.to_numeric(df["remainLayer"], errors='coerce')
            df["layerCount"] = pd.to_numeric(df["layerCount"], errors='coerce')

            # 将purchaseOrder为空的数据改为Trail
            trail_mask = df["purchaseOrder"] == " "
            df.loc[trail_mask, "purchaseOrder"] = "Trail"
            df.loc[trail_mask, "itemName"] = "Trail"

            # 安全计算currentPosition
            df["currentPosition"] = df.apply(
                lambda row: row["layerCount"] - row["remainLayer"]
                if pd.notna(row["layerCount"]) and pd.notna(row["remainLayer"])
                else None,
                axis=1
            )

            # 安全转换日期
            df["forecastDate"] = pd.to_datetime(df["forecastDate"], errors='coerce') + pd.Timedelta(days=7)

            df = df[data_format]
            self.logger.debug(f"成功处理荣芯Excel文件")
            return df
        except Exception as e:
            self.logger.error(f"处理荣芯Excel文件失败: {e}")
            return None

