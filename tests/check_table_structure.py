import sys
import os
import logging
from sqlalchemy import text

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.database import DatabaseSession

# 设置基本的日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_structure():
    """查看表结构"""
    try:
        with DatabaseSession() as session:
            # 查询表结构
            columns = session.execute(text("""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    IS_NULLABLE,
                    COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'huaxinAdmin_wip_fab'
                ORDER BY ORDINAL_POSITION
            """)).fetchall()
            
            logger.info("huaxinAdmin_wip_fab 表结构:")
            for col in columns:
                col_type = f"{col[1]}"
                if col[2]:  # 如果有长度
                    col_type += f"({col[2]})"
                nullable = "NULL" if col[3] == "YES" else "NOT NULL"
                default = f"DEFAULT {col[4]}" if col[4] else ""
                
                logger.info(f"- {col[0]}: {col_type} {nullable} {default}")
                
    except Exception as e:
        logger.error(f"查询表结构失败: {str(e)}", exc_info=True)

if __name__ == "__main__":
    check_table_structure() 