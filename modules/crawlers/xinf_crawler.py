"""
江苏芯丰爬虫模块
"""

from datetime import datetime
from typing import Optional, Dict, Any
from .base_crawler import BaseCrawler
import os
import pandas as pd

class XinfCrawler(BaseCrawler):
    """爬取江苏芯丰WIP数据"""
    
    # 基础URL
    BASE_URL = "http://36.133.174.185:8081" # pws/sys/customLogin
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化江苏芯丰爬虫
        
        Args:
            config: 配置参数
        """
        super().__init__(config)
        
        # 更新请求头
        self.headers.update({
            "Content-Type": "application/json;charset=UTF-8"
        })
        
        self.session.trust_env = False
        self._token = None

    def login(self) -> bool:
        """
        登录系统
        
        Returns:
            bool: 登录是否成功
        """
        try:
            self.logger.info("开始登录江苏芯丰PWS系统...")
            login_url = f"{self.BASE_URL}/pws/sys/customLogin"
            
            login_data = {
                "username": self.config["username"], 
                "password": self.config["password"], 
                "remember_me": self.config.get("remember_me", True)
            }
            
            response = self.post(login_url, json=login_data)
            response.raise_for_status()
            
            # 获取token
            response_data = response.json()
            if response_data.get("success") and "result" in response_data and "token" in response_data["result"]:
                self._token = response_data["result"]["token"]
                # 更新请求头，添加token
                self.headers.update({
                    "X-Access-Token": self._token
                })
                self.logger.info("登录成功并获取token")
            else:
                self.logger.error(f"登录响应格式错误: {response_data}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"登录失败: {str(e)}")
            return False

    def get_wip_data(self) -> bool:
        """
        获取WIP数据并保存为Excel
        
        Returns:
            bool: 是否成功获取并保存数据
        """
        try:
            if not self._token:
                self.logger.error("未获取到token，请先登录")
                return False
                
            self.logger.info("开始获取WIP数据...")
            
            # 构建请求参数
            params = {
                "_t": str(int(datetime.now().timestamp() * 1000)),  # 使用当前时间戳
                "field": "id,cardCode,packageCode,pmodel,currentqty,stepName,arriveTimestamp,waferModel,waferBatch,workOrderCode,startDate,manufaturingType_dictText,priority_dictText,customerSoCode,customerCode",
                "pageNo": 1,
                "pageSize": 150
            }
            
            # 访问在制明细页面
            wip_detail_url = f"{self.BASE_URL}/pws/web/webMesCardWip/list"
            response = self.get(wip_detail_url, params=params)
            
            # 检查是否需要重新登录
            if response.status_code == 500 and "Token失效" in response.text:
                self.logger.info("Token已失效，尝试重新登录...")
                if self.login():
                    # 重新发送请求
                    response = self.get(wip_detail_url, params=params)
                    response.raise_for_status()
                else:
                    return False
            else:
                response.raise_for_status()
            
            # 获取数据
            data = response.json()
            
            if not data.get("success"):
                self.logger.error(f"获取数据失败: {data.get('message', '未知错误')}")
                return False
                
            records = data.get("result", {}).get("records", [])
            
            # 获取输出目录
            output_dir = self.config.get("output_dir", "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 生成文件名
            date = datetime.now().strftime("%Y%m%d")
            filename = os.path.join(output_dir, f"江苏芯丰_{date}.xlsx")
            
            # 将数据转换为DataFrame并保存为Excel
            if not records:
                self.logger.info("获取的数据记录为空，创建空文件")
                # 创建一个空的DataFrame，保持列名一致
                columns = ["row", "cardCode", "packageCode", "pmodel", "currentqty", 
                          "stepName", "arriveTimestamp", "waferModel", "waferBatch", 
                          "workOrderCode", "startDate", "manufaturingType_dictText", 
                          "priority_dictText", "customerSoCode", "customerCode"]
                df = pd.DataFrame(columns=columns)
            else:
                df = pd.DataFrame(records)
                
            df.to_excel(filename, index=False, engine='openpyxl')
            
            self.logger.info(f"数据已保存到: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"获取WIP数据失败: {str(e)}")
            # 保存错误响应内容
            try:
                with open("logs/error_response.txt", "w", encoding="utf-8") as f:
                    f.write(f"URL: {response.url}\n")
                    f.write(f"Status Code: {response.status_code}\n")
                    f.write(f"Headers: {response.headers}\n")
                    f.write(f"Content: {response.text}")
            except:
                pass
            return False
    
    def run(self) -> bool:
        """运行爬虫任务"""
        if not self.login():
            return False
            
        # 获取数据
        return self.get_wip_data()

def main():
    """主函数"""
    try:
        # 创建爬虫实例
        crawler = XinfCrawler(username="314", password="68241373")
        
        # 运行爬虫
        if not crawler.run():
            return
        
    except Exception as e:
        crawler.logger.error(f"程序执行出错: {str(e)}")

if __name__ == "__main__":
    main()
