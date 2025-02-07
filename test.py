import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import load_yaml

path = r"C:\Users\18020\Downloads\苏州华芯微电子股份有限公司的封装产品进展表2025-02-07.xlsx"
# path_2 = r"C:\Users\18020\Downloads\华芯微WIP.xlsx"


config = load_yaml("config/wip_fields.yaml")
data_format = config["wip_fields"]["封装厂"]["craft_forecast"]
key_columns = config["wip_fields"]["封装厂"]["池州华宇"]["关键字段映射"]
# key_columns = config["wip_fields"]["封装厂"]["山东汉旗"]["关键字段映射"]
mapping_dict = {k: v for k, v in key_columns.items()}

# df = pd.read_excel(path_2, header=0)
df = pd.read_excel(path, header=0)

df = df[list(key_columns.keys())]

# df.rename(columns=mapping_dict, inplace=True)
# df = df[data_format]
# # 获取除第一列外的所有列
# # numeric_columns = df.columns[1:]


# # 将这些列转换为整数类型,错误值和空值设为0
# # for col in numeric_columns:
# #     df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# print(df)


print(df)
