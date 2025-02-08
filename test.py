import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import load_yaml

config = load_yaml("config/wip_fields.yaml").get("wip_fields").get("封装厂").get("池州华宇")
craft_forecast = load_yaml("config/wip_fields.yaml").get("wip_fields").get("封装厂").get("craft_forecast")
data_format = load_yaml("config/wip_fields.yaml").get("wip_fields").get("封装厂").get("data_format")

key_columns = self.config["关键字段映射"]


file_path = r"\\Xinxf\池州华宇进度表\苏州华芯微电子股份有限公司的封装产品进展表2025-02-08.xlsx"

df = pd.read_excel(file_path, header=0)

df = df[list(fz_fields.keys())]

df.rename(columns=fz_fields, inplace=True)

numerical_columns = list(craft_forecast.keys())
df[numerical_columns] = df[numerical_columns].apply(pd.to_numeric, errors='coerce')

print(df[numerical_columns])

# 从后往前遍历numerical_columns，找到第一个值大于0的列名
df["当前工序"] = df[numerical_columns[::-1]].apply(
    lambda row: next(
        (col for col in numerical_columns[::-1] if row[col] > 0),
        None
    ),
    axis=1
)

# 根据当前工序，计算预计完成时间
df["预计交期"] = df["当前工序"].apply(
    lambda x: pd.Timestamp.now().date() + pd.Timedelta(days=craft_forecast.get(x, 0)) if x else pd.NaT
)

print(df[["订单号", "当前工序", "预计交期"]])

tomorrow_columns = [k for k, v in craft_forecast.items() if v <= 1]
three_days_columns = [k for k, v in craft_forecast.items() if v <= 3]
seven_days_columns = [k for k, v in craft_forecast.items() if v <= 7]

df["次日预计"] = df[tomorrow_columns].sum(axis=1, min_count=1)
df["三日预计"] = df[three_days_columns].sum(axis=1, min_count=1)
df["七日预计"] = df[seven_days_columns].sum(axis=1, min_count=1)

df.to_json(r"C:\Users\admin\Desktop\output.json", orient="records", force_ascii=False)

# print(tomorrow_columns)
# print(three_days_columns)
# print(seven_days_columns)

