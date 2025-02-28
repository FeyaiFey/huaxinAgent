import pandas as pd

df = pd.read_excel(r'C:\Users\admin\Desktop\HuaXin  WIP&Stock Report_20250228.xls', header=0, sheet_name="WIP Report")
df_stock = pd.read_excel(r'C:\Users\admin\Desktop\HuaXin  WIP&Stock Report_20250228.xls', header=0, sheet_name="Stock")

field_dict = {"Customer\nDevice":"itemName","Lot ID":"lot","Qty":"qty","Date":"forecastDate"}
df_stock.rename(columns=field_dict, inplace=True)
df_stock = df_stock[["itemName","lot","qty","forecastDate"]]

print(df_stock)

