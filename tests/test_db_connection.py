import sys
import os
from sqlalchemy import text

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.database import DatabaseSession, DatabaseManager
from utils.logger import Logger

# 设置基本的日志配置
logger = Logger(__name__)

def test_database_connection():
    """测试数据库连接"""
    try:
        # 测试数据库管理器初始化
        db_manager = DatabaseManager()
        logger.info("数据库管理器初始化成功")
        
        # 测试会话创建和查询
        with DatabaseSession() as session:
            # 执行一个简单的SQL查询
            result = session.execute(text("SELECT @@VERSION")).scalar()
            logger.info(f"SQL Server 版本: {result}")
            
            # 测试数据库名称
            db_name = session.execute(text("SELECT DB_NAME()")).scalar()
            logger.info(f"当前数据库: {db_name}")
            
            # 测试表列表
            tables = session.execute(text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """)).fetchall()
            
            logger.info("数据库中的表:")
            for table in tables:
                logger.info(f"- {table[0]}")
                
        logger.info("数据库连接测试完成")
        return True
        
    except Exception as e:
        logger.error(f"数据库连接测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("开始测试数据库连接...")
    success = test_database_connection()
    if success:
        logger.info("数据库连接测试成功!")
    else:
        logger.error("数据库连接测试失败!") 