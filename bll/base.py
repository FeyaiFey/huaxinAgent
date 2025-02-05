from typing import TypeVar, Generic, Type
from dal.base import BaseDAL
from models.base import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseBLL(Generic[T]):
    """基础业务逻辑类"""
    
    def __init__(self, dal_class: Type[BaseDAL]):
        """
        初始化
        Args:
            dal_class: 数据访问层类
        """
        self.dal = dal_class() 