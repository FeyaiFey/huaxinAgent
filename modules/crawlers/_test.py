import requests
import os
import urllib3
from urllib.parse import urlencode

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 禁用系统代理
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

# 创建会话
session = requests.Session()

# 配置会话
session.trust_env = False  # 不使用环境变量中的代理设置
proxies = {
    'http': None,
    'https': None
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://my2.hjtc.com.cn/myhj_web/Production/WIP/summary_drill"
}

try:
    # 1. 登录系统
    login_url = "https://my2.hjtc.com.cn/secure/login_hjtc.fcc?TYPE=33554433&REALMOID=06-af713708-e650-4979-afd0-d504ff745fd2&GUID=0&SMAUTHREASON=0&METHOD=GET&SMAGENTNAME=-SM-oEHd7jdu1MRiPlIRQQWzhpTe%2bzCsgXutiNAm67JlRwA9yMKTNX1H5EwwnharNAiE&TARGET=-SM-https%3a%2f%2fmy2%2ehjtc%2ecom%2ecn%2f"
    login_data = {
        "username": "HUX_LEIHJ",
        "password": "UNBfg-241113"
    }

    response = session.post(
        login_url,
        data=login_data,
        headers=headers,
        proxies=proxies,
        verify=False,
        timeout=30
    )
    response.raise_for_status()
    print("登录成功！")

    # 2. 先访问summary_drill页面
    summary_url = "https://my2.hjtc.com.cn/myhj_web/Production/WIP/summary_drill"
    response = session.get(
        summary_url,
        headers=headers,
        proxies=proxies,
        verify=False,
        timeout=30
    )
    response.raise_for_status()
    print("访问summary页面成功")

    # 3. 获取数据集
    dataset_url = "https://my2.hjtc.com.cn/myhj_web/Production/WIP/summary_dataset_grid"
    
    # 修改请求参数格式
    dataset_params = {
        "DXScript": "1_187,1_101,1_180,1_120,1_182,1_155,1_154,17_34,17_13",
        "DXCss": "/myhj_web/App_Themes/MyUMC/DevExpress.css,/myhj_web/App_Themes/MyUMC/GridView.css",
        "RequiredFields": "FAB_ID,LOT,WIP_QTY",
        "OptionalFields": "STAGE,PO,PROCESS,PROCESSVERSION,WAFER_NO,SITE_LOT,CUSTOMERLOT,SHP_PRD_NO,CUST_PART,CTM_DEVICE,ROUTEDESC,ROUTESEQUENCE,IN_TIME,LOTTYPE,DIE_QTY,WS_DATE,SHIP_CONF_DATE,SHIP_FCST_DATE,PRIORITY,LOTSTATUS,RETICLEVERSION,PROCESSGEN,PROCESSFAMILY,SUBCONTRACT,RELEASE_PO,PRD_NO,ROUTEPOSITION,FUTURE_HOLD_LAYER,WS_QTY,GROSS_DIE,WO_FCST_DATE,WO_DATE,STAY_DAY,BACK_DAY,SHIPTO_ID,LAYER,LAYER_POSITION,FUTURE_HOLD_LAYER_POSITION,FUTURE_HOLD_FLAG,MTH_NO,HOLDDAYS,HOLDBEGINTMST,CONFIRM_DESCRIPTION as CONF_DESC,DIRECT_PO",
        "ReportCategory": "ALL",
        "Fabs": "FAB8N",
        "Stages": "ALL",
        "CustomerPartType": "1",
        "CustomerParts": "ALL",
        "ShippingProductType": "1",
        "ShippingProducts": "ALL",
        "UmcProductType": "1",
        "UmcProducts": "ALL",
        "__RequestVerificationToken": "kuEVVxLx9-ukDkjgeZPBGLdnlbYYzXg-RZqbZ3kWSfcFQMNWQE3y2uH-YljbahXGz0EIbM_B-Iw61gH6PXjQWtwoGWV-rFEf2h2alfaSuzg1"
    }
    
    response = session.post(
        dataset_url,
        data=dataset_params,
        headers=headers,
        proxies=proxies,
        verify=False,
        timeout=30
    )
    response.raise_for_status()
    print("获取数据集成功")

    # 4. 访问excel下载url,下载excel
    download_url = "https://my2.hjtc.com.cn/myhj_web/Production/WIP/summary_drill_export"
    download_data = {
        "Fab": "FAB8N",
        "Stage": "ALL",
        "ReportCategory": "ALL",
        "CustomerPartType": "1",
        "CustomerParts": "ALL",
        "ShippingProductType": "1",
        "ShippingProducts": "ALL",
        "UmcProductType": "1",
        "UmcProducts": "ALL"
    }
    
    response = session.post(
        download_url,
        data=download_data,
        headers=headers,
        proxies=proxies,
        verify=False,
        timeout=30
    )
    response.raise_for_status()
    
    # 获取文件名
    from datetime import datetime
    filename = f"WIP_SUMMARY_{datetime.now().strftime('%Y%m%d%H%M')}00.csv"
    
    # 将响应内容保存为Excel文件
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f"Excel文件已下载保存为: {filename}")

except requests.exceptions.RequestException as e:
    print(f"请求出错: {str(e)}")
except Exception as e:
    print(f"发生错误: {str(e)}")
    import traceback
    print(traceback.format_exc())
