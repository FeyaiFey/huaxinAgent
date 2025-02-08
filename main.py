"""
华芯自动化代理系统
主入口文件
"""

import os
import sys
import signal
import time
from pathlib import Path
from dotenv import load_dotenv
from utils.logger import Logger
from core.scheduler import Scheduler

class HuaxinAgent:
    """华芯自动化代理系统主类"""
    
    def __init__(self):
        """初始化系统"""
        self.logger = Logger(__name__)
        self.logger.info("开始运行华芯自动化代理系统...")
        self._init_environment()
        self.scheduler = Scheduler()
        self.running = False
        
    def _init_environment(self):
        """初始化环境"""
        try:
            # 加载环境变量
            env_path = Path('.env')
            if env_path.exists():
                load_dotenv(env_path)
                self.logger.debug("环境变量加载成功")
            else:
                self.logger.warning("未找到.env文件，请确保环境变量已正确设置")
            
            # 创建必要的目录
            directories = ['logs', 'attachments']
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
                
        except Exception as e:
            self.logger.error(f"初始化环境失败: {str(e)}", exc_info=True)
            raise
            
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            self.logger.info(f"收到信号: {signum}")
            self.stop()
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def start(self):
        """启动系统"""
        try:
            self._setup_signal_handlers()
            self.scheduler.start()
            self.running = True
            
            # 输出任务状态
            jobs_status = self.scheduler.get_jobs_status()
            for job_id, status in jobs_status.items():
                self.logger.debug(
                    f"任务 {status['name']} 下次运行时间: "
                    f"{status['next_run_time']}"
                )
            
            # 保持主线程运行
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"系统启动失败: {str(e)}", exc_info=True)
            self.stop()
            sys.exit(1)
            
    def stop(self):
        """停止系统"""
        try:
            self.logger.info("正在停止华芯自动化代理系统...")
            self.running = False
            self.scheduler.stop()
            self.logger.info("系统已停止")
            
        except Exception as e:
            self.logger.error(f"系统停止失败: {str(e)}", exc_info=True)
            sys.exit(1)

def main():
    """主函数"""
    agent = HuaxinAgent()
    try:
        agent.start()
    except KeyboardInterrupt:
        agent.stop()
    except Exception as e:
        Logger(__name__).error(f"系统运行异常: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
