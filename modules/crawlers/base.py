"""
基础爬虫类模块
提供所有爬虫的基础功能
"""

from typing import Dict, List, Any
import os
import requests
import urllib3
from utils.logger import Logger
from utils.helpers import get_env_var
class BaseCrawler:
    """基础爬虫类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化基础爬虫
        
        Args:
            config: 爬虫配置
        """
        # 初始化日志记录器
        self.logger = Logger(__name__)
        
        # 创建session
        self.session = requests.Session()
        self.config = self._replace_env_vars(config)
        
        # 禁用SSL警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # 基础请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        
        # 代理设置
        self.proxies = {
            'http': None,
            'https': None
        }
        
        # 禁用系统代理
        self._disable_system_proxy()

        self.session.trust_env = False
        
        # self.logger.info("爬虫初始化完成")

    def _replace_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """替换配置文件中的环境变量"""
        for key, value in config.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                config[key] = get_env_var(env_var, value)
        return config
    
    def _disable_system_proxy(self):
        """禁用系统代理"""
        os.environ['NO_PROXY'] = '*'
        os.environ['no_proxy'] = '*'
        os.environ['HTTP_PROXY'] = ''
        os.environ['HTTPS_PROXY'] = ''
        os.environ['http_proxy'] = ''
        os.environ['https_proxy'] = ''
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """发送GET请求"""
        return self.session.get(
            url,
            headers=self.headers,
            proxies=self.proxies,
            verify=False,
            timeout=30,
            **kwargs
        )
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """发送POST请求"""
        return self.session.post(
            url,
            headers=self.headers,
            proxies=self.proxies,
            verify=False,
            timeout=30,
            **kwargs
        )
    
    def save_file(self, content: bytes, filename: str, output_dir: str) -> str:
        """
        保存文件
        
        Args:
            content: 文件内容
            filename: 文件名
            output_dir: 输出目录
            
        Returns:
            str: 保存的文件路径
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(content)
        return filepath
    
    def run(self):
        """
        运行爬虫任务
        子类必须实现此方法
        """
        raise NotImplementedError("子类必须实现run方法") 