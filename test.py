import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import load_yaml

path = r"\\Xinxf\池州华宇进度表\苏州华芯微电子股份有限公司的封装产品进展表2025-01-24.xlsx"

config = load_yaml("config/wip_fields.yaml")
data_format = config["wip_fields"]["封装厂"]["data_format"]
key_columns = config["wip_fields"]["封装厂"]["池州华宇"]["关键字段映射"]
mapping_dict = {k: v for k, v in key_columns.items()}

df = pd.read_excel(path, header=0, sheet_name="Sheet1")

df = df[list(key_columns.keys())]

df.rename(columns=mapping_dict, inplace=True)
print(df)
