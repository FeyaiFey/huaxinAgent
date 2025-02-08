import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import load_yaml

config = load_yaml("config/wip_fields.yaml").get("wip_fields").get("封装厂").get("山东汉旗")
craft_forecast = load_yaml("config/wip_fields.yaml").get("wip_fields").get("封装厂").get("craft_forecast")
data_format = load_yaml("config/wip_fields.yaml").get("wip_fields").get("封装厂").get("data_format")

key_columns = config["关键字段映射"]
names = list(key_columns.keys())


file_path = r"C:\Users\admin\Desktop\华芯微WIP.xlsx"

df = pd.read_excel(file_path, header=0)

# 清理列名中的空格
df.columns = df.columns.str.strip()

df = df[names]

key_columns = {k.strip(): v for k, v in key_columns.items()}


print(df.columns)



# 创建映射字典并重命名列
mapping_dict = {k: v for k, v in key_columns.items()}
df.rename(columns=mapping_dict, inplace=True)

# 整理数据
marking_columns = ["Mar_king打印", "打印前烘烤"]
df[marking_columns] = df[marking_columns].apply(pd.to_numeric, errors='coerce').fillna(0)
df["打印"] = df[marking_columns].sum(axis=1, min_count=1)

test_columns = ["测试打印", "测试编带", "测试管装", "编带"]
df[test_columns] = df[test_columns].apply(pd.to_numeric, errors='coerce').fillna(0)
df["测编打印"] = df[test_columns].sum(axis=1, min_count=1)


df[["研磨","切割","待装片","等离子清洗1","三目检","等离子清洗2","回流焊","后切割","切筋成型","外观检","包装","待入库"]] = 0

df["扣留信息"] = pd.NaT

numerical_columns = list(craft_forecast.keys())
df[numerical_columns] = df[numerical_columns].apply(pd.to_numeric, errors='coerce')

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

print(df)
# print(tomorrow_columns)
# print(three_days_columns)
# print(seven_days_columns)

