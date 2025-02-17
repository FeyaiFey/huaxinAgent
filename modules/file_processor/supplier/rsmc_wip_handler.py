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
                
                # 清理列名中的空格
                df.columns = df.columns.str.strip()
                
                # 检查是否包含所需的列
                missing_columns = set(name_values) - set(df.columns)
                if missing_columns:
                    self.logger.error(f"Excel文件缺少必要的列: {missing_columns}")
                    self.logger.debug(f"现有列: {list(df.columns)}")
                    self.logger.debug(f"需要的列: {name_values}")
                    return None
                    
            except ValueError as e:
                if "No sheet named" in str(e):
                    self.logger.error("Excel文件中没有名为'WIP Report'的工作表")
                    return None
                raise
            
            # 只选择需要的列
            try:
                df = df[name_values]
            except KeyError as e:
                self.logger.error(f"选择列时出错: {str(e)}")
                self.logger.debug(f"现有列: {list(df.columns)}")
                self.logger.debug(f"尝试选择的列: {name_values}")
                return None

            # 创建反向映射字典
            reverse_names = {v.strip(): k.strip() for k, v in names.items()}
            
            # 重命名列
            try:
                df.rename(columns=reverse_names, inplace=True)
            except Exception as e:
                self.logger.error(f"重命名列时出错: {str(e)}")
                self.logger.debug(f"重命名映射: {reverse_names}")
                return None

            df["supplier"] = "荣芯"
            df["finished_at"] = pd.NaT

            # 处理数值型字段，将非数值转换为NaN
            try:
                df["remainLayer"] = pd.to_numeric(df["remainLayer"], errors='coerce')
                df["layerCount"] = pd.to_numeric(df["layerCount"], errors='coerce')
            except Exception as e:
                self.logger.error(f"转换数值字段时出错: {str(e)}")
                return None

            # 将purchaseOrder为空的数据改为Trail
            trail_mask = df["purchaseOrder"].isna() | (df["purchaseOrder"].str.strip() == "")
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
            try:
                df["forecastDate"] = pd.to_datetime(df["forecastDate"], errors='coerce')
                # 只对非空日期进行偏移计算
                df["forecastDate"] = df["forecastDate"].apply(
                    lambda x: (x + pd.Timedelta(days=7)).date() if pd.notna(x) else pd.NaT
                )
            except Exception as e:
                self.logger.error(f"转换日期字段时出错: {str(e)}")
                return None

            # 确保数据格式正确
            try:
                df = df[data_format]
            except KeyError as e:
                self.logger.error(f"整理最终数据格式时出错: {str(e)}")
                self.logger.debug(f"现有列: {list(df.columns)}")
                self.logger.debug(f"需要的列: {data_format}")
                return None

            self.logger.debug(f"成功处理荣芯Excel文件")
            return df
            
        except Exception as e:
            self.logger.error(f"处理荣芯Excel文件失败: {str(e)}")
            return None

