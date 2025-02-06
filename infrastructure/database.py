from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
import os
from threading import Lock

from utils.logger import Logger
from utils.retry import retry_network
from utils.helpers import load_yaml, get_env_var


class DatabaseManager:
    """数据库管理类，负责处理与数据库的连接和会话管理"""
    
    _instance: Optional['DatabaseManager'] = None
    _engine: Optional[Engine] = None
    _session_maker: Optional[sessionmaker] = None
    _lock = Lock()
    
    def __new__(cls) -> 'DatabaseManager':
        """单例模式实现"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """初始化数据库管理器"""
        self.logger = Logger(__name__)
        if self._engine is None:
            self._initialize()
    
    @retry_network
    def _initialize(self) -> None:
        """初始化数据库连接"""
        try:
            # 读取配置文件
            config_path = os.path.join('config', 'settings.yaml')
            config = load_yaml(config_path)
            db_config = config['database']
            
            # 身份验证方式
            auth_type = db_config.get('auth_type', 'windows')
            
            # 构建连接字符串
            server = db_config.get('server', 'localhost')
            database = db_config.get('database', 'master')
            driver = db_config.get('driver', 'ODBC Driver 17 for SQL Server')
            
            if auth_type.lower() == 'sql':
                # SQL Server 身份验证
                username = get_env_var('DB_USER', db_config.get('username'))
                password = get_env_var('DB_PASSWORD', db_config.get('password'))
                conn_str = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"UID={username};"
                    f"PWD={password};"
                    f"TrustServerCertificate=yes"
                )
            else:
                # Windows 身份验证
                conn_str = (
                    f"DRIVER=ODBC Driver 17 for SQL Server;"
                    f"SERVER=localhost;"
                    f"DATABASE={database};"
                    f"Trusted_Connection=yes;"
                    f"TrustServerCertificate=yes"
                )
            
            self.logger.debug(f"使用 {auth_type} 认证方式连接数据库")
            
            # 创建引擎
            self._engine = create_engine(
                f"mssql+pyodbc:///?odbc_connect={conn_str}",
                poolclass=QueuePool,
                pool_size=int(get_env_var('DB_POOL_SIZE', '5')),
                max_overflow=int(get_env_var('DB_MAX_OVERFLOW', '10')),
                pool_timeout=int(get_env_var('DB_POOL_TIMEOUT', '30')),
                pool_recycle=int(get_env_var('DB_POOL_RECYCLE', '3600')),
                echo=db_config.get('echo', False)
            )
            
            # 创建会话工厂
            self._session_maker = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False
            )
            
            self.logger.debug(f"数据库连接池初始化成功: {server}/{database}")
            
        except Exception as e:
            self.logger.error(f"数据库连接池初始化失败: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        if self._session_maker is None:
            raise RuntimeError("数据库会话工厂未初始化")
        return self._session_maker()
    
    def close_all(self) -> None:
        """关闭所有连接"""
        if self._engine:
            self._engine.dispose()
            self.logger.info("数据库连接池已关闭")

class DatabaseSession:
    """数据库会话上下文管理器"""
    
    def __init__(self):
        self.logger = Logger(__name__)
        self.db = DatabaseManager()
        self.session: Optional[Session] = None
    
    def __enter__(self) -> Session:
        """进入上下文，返回会话对象"""
        self.session = self.db.get_session()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文，处理会话清理"""
        if self.session:
            try:
                if exc_type is None:
                    # 如果没有异常发生，提交事务
                    self.session.commit()
                else:
                    # 如果有异常发生，回滚事务
                    self.session.rollback()
                    self.logger.error(f"数据库操作失败: {str(exc_val)}")
            except SQLAlchemyError as e:
                self.session.rollback()
                self.logger.error(f"数据库事务处理失败: {str(e)}")
            finally:
                self.session.close()

# 使用示例
"""
# 方式1：使用上下文管理器（推荐）
with DatabaseSession() as session:
    try:
        # 执行数据库操作
        result = session.query(SomeModel).all()
        # 不需要手动提交，上下文管理器会自动处理
    except SQLAlchemyError as e:
        # 异常会被上下文管理器捕获并处理
        logger.error(f"查询失败: {str(e)}")

# 方式2：直接使用数据库管理器
try:
    db = DatabaseManager()
    session = db.get_session()
    # 执行数据库操作
    result = session.query(SomeModel).all()
    session.commit()
except SQLAlchemyError as e:
    session.rollback()
    logger.error(f"查询失败: {str(e)}")
finally:
    session.close()
"""
