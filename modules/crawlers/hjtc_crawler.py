"""
和舰科技爬虫模块
"""

from datetime import datetime
import os
from typing import Optional, Dict, Any
from modules.crawlers.base import BaseCrawler
from modules.file_processor.hjtc_handler import process_hjtc_excel
from bll.wip_fab import WipFabBLL

class HJTCCrawler(BaseCrawler):
    """
    和舰科技爬虫类,用于爬取和舰科技的WIP数据
    
    主要功能:
    1. 登录和舰科技系统
    2. 爬取WIP数据
    3. 处理并保存数据
    
    属性:
        BASE_URL: 和舰科技系统的基础URL
        headers: 请求头信息
        session: 会话对象,用于维持登录状态
        config: 配置信息,包含用户名密码等
        logger: 日志记录器
        
    方法:
        login(): 登录系统
        get_wip_data(): 获取WIP数据
        process_data(): 处理爬取的数据
        run(): 执行爬虫任务
        
    使用示例:
        crawler = HJTCCrawler(config)
        crawler.run()
    """
    
    # 基础URL
    BASE_URL = "https://my2.hjtc.com.cn"
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化和舰科技爬虫
        
        Args:
            config: 配置参数
        """
        super().__init__(config)
        
        # 更新请求头
        self.headers.update({
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", 
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.BASE_URL}/myhj_web/Production/WIP/summary_drill"
        })
        
        self.session.trust_env = False

    def login(self) -> bool:
        """
        登录系统
        
        Returns:
            bool: 登录是否成功
        """
        try:
            self.logger.info("开始登录和舰科技系统...")
            login_url = f"{self.BASE_URL}/secure/login_hjtc.fcc?TYPE=33554433&REALMOID=06-af713708-e650-4979-afd0-d504ff745fd2&GUID=0&SMAUTHREASON=0&METHOD=GET&SMAGENTNAME=-SM-oEHd7jdu1MRiPlIRQQWzhpTe%2bzCsgXutiNAm67JlRwA9yMKTNX1H5EwwnharNAiE&TARGET=-SM-https%3a%2f%2fmy2%2ehjtc%2ecom%2ecn%2f"
            
            login_data = {
                "username": self.config["username"],
                "password": self.config["password"]
            }
            
            response = self.post(login_url, data=login_data)
            response.raise_for_status()
            
            self.logger.info("登录成功")
            return True
            
        except Exception as e:
            self.logger.error(f"登录失败: {str(e)}")
            return False

    # def get_wip_data(self) -> Optional[Dict]:
    #     """
    #     获取WIP数据
        
    #     Returns:
    #         Optional[Dict]: WIP数据，失败返回None
    #     """
    #     try:
    #         self.logger.info("开始获取WIP数据...")
            
    #         # 访问summary页面
    #         summary_url = f"{self.BASE_URL}/myhj_web/Production/WIP/summary_drill"
    #         response = self.get(summary_url)
    #         response.raise_for_status()
            
    #         self.logger.info("访问summary页面成功")
            
    #         # 获取数据
    #         dataset_url = f"{self.BASE_URL}/myhj_web/Production/WIP/summary_dataset_grid"
    #         dataset_data = {
    #             "Fab": "FAB8N",
    #             "Stage": "ALL",
    #             "ReportCategory": "ALL",
    #             "CustomerPartType": "1",
    #             "CustomerParts": "ALL",
    #             "ShippingProductType": "1",
    #             "ShippingProducts": "ALL",
    #             "UmcProductType": "1",
    #             "UmcProducts": "ALL"
    #         }
            
    #         response = self.post(dataset_url, data=dataset_data)
    #         response.raise_for_status()
            
    #         self.logger.info("获取WIP数据成功")
    #         return response.json()
            
    #     except Exception as e:
    #         self.logger.error(f"获取WIP数据失败: {str(e)}")
    #         return None

    def download_wip_excel(self) -> Optional[str]:
        """
        下载WIP Excel报表
        
        Returns:
            Optional[str]: 下载的文件路径，失败返回None
        """
        try:
            self.logger.info("开始下载WIP Excel报表...")
            
            # 下载Excel
            download_url = f"{self.BASE_URL}/myhj_web/Production/WIP/summary_drill_export"
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
            
            # 修改headers添加Excel相关的Accept
            self.headers["Accept"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            response = self.post(download_url, data=download_data)
            response.raise_for_status()
            
            # 保存文件
            date = datetime.now().strftime("%Y%m%d")
            filename = f"和舰科技_{date}.csv"
            filepath = self.save_file(response.content, filename, self.config["output_dir"])
            self.logger.info(f"Excel文件已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"下载Excel失败: {str(e)}")
            return None
    
    def run(self) -> bool:
        """运行爬虫任务"""
        if not self.login():
            return False
            
        # 获取数据
        # data = self.get_wip_data()
        # if not data:
        #     return False
        
        # 下载Excel
        filepath = self.download_wip_excel()

        # 处理Excel
        df = process_hjtc_excel(filepath)
        if not (df is not None and not df.empty):
            self.logger.error(f"处理Excel失败")
            return False

        # 将数据merge到sqlserver
        # with DBProcessor() as db_processor:
        #     if not db_processor.merge_to_db(df, "huaxinAdmin_wip_fab"):
        #         self.logger.error(f"合并数据到sqlserver失败")
        #         return False
        # try:
        #     os.remove(filepath)
        # except Exception as e:
        #     self.logger.error(f"删除文件失败: {str(e)}")
        return True