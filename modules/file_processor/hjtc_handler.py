import os
import pandas as pd
from typing import Dict, List, Optional, Any
from utils.logger import Logger
from utils.helpers import load_yaml

def process_hjtc_excel(file_path: str) -> Optional[str]:
    """
    处理和舰科技Excel文件
    
    Args:
        file_path: 要处理的Excel文件路径
        
    Returns:
        Optional[str]: 处理后的文件路径，如果处理失败则返回None
    """
    logger = Logger(__name__)
    fields_config = load_yaml("config/wip_fields.yaml")
    crawler_config = load_yaml("config/crawler_config.yaml")
    try:
        header = fields_config["wip_fields"]["晶圆厂"]["和舰科技"]["header"]
        names = fields_config["wip_fields"]["晶圆厂"]["和舰科技"]["names"]
        name_values = list(names.values())
        data_format = fields_config["wip_fields"]["data_format"]
        df = pd.read_csv(file_path, header=header , encoding='utf-8')
        df = df[name_values]
        df.rename(columns=names, inplace=True)
        # 创建反向映射字典
        reverse_names = {v: k for k, v in names.items()}
        # 重命名列
        df.rename(columns=reverse_names, inplace=True)
        df["layerCount"] = (df["layerCount"]/1000).astype(int)
        df["remainLayer"] = df["layerCount"] - df["currentPisition"]
        df["forecastDate"] = pd.to_datetime(df["forecastDate"]) + pd.Timedelta(days=7)
        df["forecastDate"] = df["forecastDate"].dt.date
        df["supplier"] = "和舰科技"
        df["finished_at"] = pd.NaT
        df = df[data_format]

        logger.info(f"成功处理和舰科技Excel文件")
        return df
    
    except Exception as e:
        logger.error(f"处理和舰科技Excel文件失败: {e}")
        return None

