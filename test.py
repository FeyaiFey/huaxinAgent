import pandas as pd
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import load_yaml


total_config = load_yaml("config/wip_fields.yaml")
config = total_config["wip_fields"]["晶圆厂"]["上华FAB2"]
data_format = total_config["wip_fields"]["data_format"]

path = r"C:\Users\admin\Desktop\HS-SZ_FAB2(2025-02-07).xls"

header = config["header"]
names = config["names"]
name_values = list(names.values())

try:
    # 读取CSV文件，处理编码错误
    df = pd.read_excel(path, header=header, sheet_name="wip")
    # df = df[name_values]
    # df.rename(columns=names, inplace=True)
    # # 创建反向映射字典
    # reverse_names = {v: k for k, v in names.items()}
    # # 重命名列
    # df.rename(columns=reverse_names, inplace=True)

    # df["supplier"] = "上华"
    # df["finished_at"] = pd.NaT

    print(df)

    # # 处理数值型字段，将非数值转换为NaN
    # df["remainLayer"] = pd.to_numeric(df["remainLayer"], errors='coerce')
    # df["layerCount"] = pd.to_numeric(df["layerCount"], errors='coerce')

    # # 将purchaseOrder为空的数据改为Trail
    # trail_mask = df["purchaseOrder"] == " "
    # df.loc[trail_mask, "purchaseOrder"] = "Trail"
    # df.loc[trail_mask, "itemName"] = "Trail"

    # # 安全计算currentPosition
    # df["currentPosition"] = df.apply(
    #     lambda row: row["layerCount"] - row["remainLayer"]
    #     if pd.notna(row["layerCount"]) and pd.notna(row["remainLayer"])
    #     else None,
    #     axis=1
    # )

    # # 安全转换日期
    # df["forecastDate"] = pd.to_datetime(df["forecastDate"], errors='coerce') + pd.Timedelta(days=7)

    # df = df[data_format]

    # print(df)

    # # 将layerCount列按"/"拆分，并创建新的currentPosition和layerCount列
    # df[["currentPosition", "layerCount"]] = df["layerCount"].str.split("/", expand=True)
    
    # # 将拆分后的列转换为数值类型,处理错误值为NaN
    # df["currentPosition"] = pd.to_numeric(df["currentPosition"], errors='coerce')
    # df["layerCount"] = pd.to_numeric(df["layerCount"], errors='coerce')

    # # 安全计算remainLayer
    # df["remainLayer"] = df.apply(
    #     lambda row: row["layerCount"] - row["currentPosition"]
    #     if pd.notna(row["layerCount"]) and pd.notna(row["currentPosition"])
    #     else None,
    #     axis=1
    # )

    # # 安全处理日期转换
    # df["forecastDate"] = pd.to_datetime(df["forecastDate"], errors='coerce')
    # # 只对非空日期进行偏移计算
    # df["forecastDate"] = df["forecastDate"].apply(
    #     lambda x: (x + pd.Timedelta(days=7)).date() if pd.notna(x) else pd.NaT
    # )

    # df["supplier"] = "上华FAB1"
    # df["finished_at"] = pd.NaT

    # df = df[data_format]

    # # 处理数值型字段，将非数值转换为NaN
    # df["layerCount"] = pd.to_numeric(df["layerCount"], errors='coerce')
    # df["currentPisition"] = pd.to_numeric(df["currentPisition"], errors='coerce')

    # # 安全处理日期转换
    # df["forecastDate"] = pd.to_datetime(df["forecastDate"], errors='coerce')
    # # 只对非空日期进行偏移计算
    # df["forecastDate"] = df["forecastDate"].apply(
    #     lambda x: (x + pd.Timedelta(days=7)).date() if pd.notna(x) else None
    # )

    # df["supplier"] = "和舰科技"
    # df["finished_at"] = pd.NaT

    # # 处理STOCK状态
    # stock_mask = df["status"].str.contains("STOCK", na=False)
    # df.loc[stock_mask, ["layerCount", "remainLayer", "currentPisition"]] = pd.NaT

    # # 安全计算remainLayer
    # df["remainLayer"] = df.apply(
    #     lambda row: row["layerCount"] - row["currentPisition"]
    #     if pd.notna(row["layerCount"]) and pd.notna(row["currentPisition"])
    #     else None,
    #     axis=1
    # )

    # # 选择需要的列
    # df = df[data_format]

    # print(df)

except FileNotFoundError:
    print(f"错误：找不到文件 {path}")
except pd.errors.EmptyDataError:
    print("错误：文件是空的")
except Exception as e:
    print(f"处理数据时发生错误: {str(e)}")


