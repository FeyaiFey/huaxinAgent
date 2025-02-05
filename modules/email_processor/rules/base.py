from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
from fnmatch import fnmatch
import re
from utils.logger import Logger

class BaseRule(ABC):
    """邮件规则基类"""
    
    def __init__(self, rule_config: Dict[str, Any]):
        """
        初始化规则
        Args:
            rule_config: 规则配置字典
        """
        self.logger = Logger(__name__)
        self.name = rule_config.get('name', '')
        self.category = rule_config.get('category', '')
        self.supplier = rule_config.get('supplier', '')
        self.conditions = rule_config.get('conditions', {})
        self.actions = rule_config.get('actions', {})
        self.enabled = rule_config.get('enabled', True)

        
    def match_pattern(self, value: Union[str, List[str]], patterns: List[str]) -> bool:
        """
        检查值是否匹配模式列表中的任意一个
        
        支持通配符匹配，如 "*@domain.com"
        
        参数:
            value: 要匹配的值（字符串或列表）
            patterns: 模式列表
            
        返回:
            bool: 是否匹配成功
        """
        if not patterns:
            return True
        if isinstance(value, list):
            return any(any(fnmatch(addr.lower(), pattern.lower()) 
                         for pattern in patterns)
                     for addr in value)
        return any(fnmatch(value.lower(), pattern.lower()) for pattern in patterns)
        
    def check_rule_conditions(self, email_data: Dict, rule: Dict) -> bool:
        """
        检查邮件是否匹配规则条件
        
        检查邮件的发件人、收件人、抄送人、主题是否满足规则中定义的条件
        所有条件都满足才返回True
        
        参数:
            email_data: 邮件数据字典
            rule: 规则字典
            
        返回:
            bool: 是否满足所有条件
        """
        conditions = rule.get('conditions', {})
        
        # 检查发件人
        if not self._check_from_condition(email_data, conditions):
            return False
            
        # 检查收件人
        if not self._check_to_condition(email_data, conditions):
            return False
            
        # 检查抄送人
        if not self._check_cc_condition(email_data, conditions):
            return False
            
        # 检查主题
        if not self._check_subject_condition(email_data, conditions):
            return False
                
        return True

    def _check_from_condition(self, email_data: Dict, conditions: Dict) -> bool:
        """检查发件人条件"""
        if 'from_contains' in conditions:
            return self.match_pattern(email_data.get('from', ''), conditions['from_contains'])
        return True

    def _check_to_condition(self, email_data: Dict, conditions: Dict) -> bool:
        """检查收件人条件"""
        if 'to_contains' in conditions:
            return self.match_pattern(email_data.get('to', []), conditions['to_contains'])
        return True

    def _check_cc_condition(self, email_data: Dict, conditions: Dict) -> bool:
        """检查抄送人条件"""
        if 'cc_contains' in conditions:
            return self.match_pattern(email_data.get('cc', []), conditions['cc_contains'])
        return True

    def _check_subject_condition(self, email_data: Dict, conditions: Dict) -> bool:
        """检查主题条件"""
        subject = email_data.get('subject', '')
        
        # 检查主题关键词
        if 'subject_contains' in conditions:
            if not any(keyword.lower() in subject.lower() 
                      for keyword in conditions['subject_contains']):
                return False
                
        # 检查主题正则表达式
        if conditions.get('subject_regex'):
            if not re.search(conditions['subject_regex'], subject):
                return False        
        return True
            
    @abstractmethod
    def process(self, email_data: Dict[str, Any]) -> bool:
        """
        处理匹配的邮件
        Args:
            email_data: 邮件数据字典
        Returns:
            处理是否成功
        """
        pass