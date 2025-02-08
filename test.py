import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import load_yaml
from modules.file_processor.supplier.rsmc_wip_handler import RsmcHandler
from bll.wip_fab import WipFabBLL

path = r"C:\Users\18020\Desktop\HuaXin  WIP&Stock Report_20250109.xls"

df = RsmcHandler().process({"attachments": [path]})

print(df)

wip_bll = WipFabBLL()
wip_bll.update_supplier_progress(df.to_dict(orient="records"))
