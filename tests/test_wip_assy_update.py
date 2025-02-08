import os
import sys
import unittest
from datetime import datetime, date
from typing import Dict, List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bll.wip_assy import WipAssyBLL
from models.wip_assy import WipAssy
from infrastructure.database import DatabaseSession

class TestWipAssyUpdate(unittest.TestCase):
    """测试WIP装配业务逻辑层的update_supplier_progress功能"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.bll = WipAssyBLL()

    def setUp(self):
        """每个测试用例开始前执行"""
        # 清理测试数据
        with DatabaseSession() as session:
            session.query(WipAssy).filter(
                WipAssy.订单号.in_(["TEST001", "TEST002"])
            ).delete(synchronize_session=False)

    def tearDown(self):
        """每个测试用例结束后执行"""
        # 清理测试数据
        with DatabaseSession() as session:
            session.query(WipAssy).filter(
                WipAssy.订单号.in_(["TEST001", "TEST002"])
            ).delete(synchronize_session=False)

    def _create_test_data(self) -> List[Dict]:
        """创建测试数据"""
        return [
            {
                "订单号": "TEST001",
                "封装厂": "池州华宇",
                "当前工序": "研磨",
                "预计交期": date.today(),
                "次日预计": 10,
                "三日预计": 20,
                "七日预计": 30,
                "仓库库存": 0,
                "扣留信息": None,
                "在线合计": 100,
                "研磨": 10,
                "切割": 0,
                "待装片": 0,
                "装片": 0,
                "银胶固化": 0,
                "等离子清洗1": 0,
                "键合": 0,
                "三目检": 0,
                "等离子清洗2": 0,
                "塑封": 0,
                "后固化": 0,
                "回流焊": 0,
                "电镀": 0,
                "打印": 0,
                "后切割": 0,
                "切筋成型": 0,
                "测编打印": 0,
                "外观检": 0,
                "包装": 0,
                "待入库": 0
            },
            {
                "订单号": "TEST002",
                "封装厂": "池州华宇",
                "当前工序": "切割",
                "预计交期": date.today(),
                "次日预计": 5,
                "三日预计": 15,
                "七日预计": 25,
                "仓库库存": 0,
                "扣留信息": None,
                "在线合计": 50,
                "研磨": 0,
                "切割": 15,
                "待装片": 0,
                "装片": 0,
                "银胶固化": 0,
                "等离子清洗1": 0,
                "键合": 0,
                "三目检": 0,
                "等离子清洗2": 0,
                "塑封": 0,
                "后固化": 0,
                "回流焊": 0,
                "电镀": 0,
                "打印": 0,
                "后切割": 0,
                "切筋成型": 0,
                "测编打印": 0,
                "外观检": 0,
                "包装": 0,
                "待入库": 0
            }
        ]

    def test_update_new_records(self):
        """测试插入新记录"""
        test_data = self._create_test_data()
        
        # 更新供应商进度
        update_stats = self.bll.update_supplier_progress(test_data)
        
        # 验证更新结果
        self.assertIsInstance(update_stats, dict, "更新统计应该是字典类型")
        self.assertGreaterEqual(update_stats['inserted'], 1, "应该至少插入一条记录")
        
        # 验证数据内容
        with DatabaseSession() as session:
            record = session.query(WipAssy).filter_by(订单号="TEST001").first()
            self.assertIsNotNone(record, "应该能找到测试记录")
            self.assertEqual(record.封装厂, "池州华宇", "供应商名称应该正确")
            self.assertEqual(record.研磨, 10, "研磨数量应该正确")
            self.assertEqual(record.当前工序, "研磨", "当前工序应该正确")
            self.assertIsInstance(record.预计交期, date, "预计交期应该是date类型")

    def test_update_existing_records(self):
        """测试更新现有记录"""
        # 先插入一条记录
        initial_data = self._create_test_data()[:1]
        self.bll.update_supplier_progress(initial_data)
        
        # 修改数据
        updated_data = initial_data.copy()
        updated_data[0]["研磨"] = 20
        updated_data[0]["当前工序"] = "切割"
        
        # 更新记录
        update_stats = self.bll.update_supplier_progress(updated_data)
        
        # 验证更新结果
        self.assertGreaterEqual(update_stats['updated'], 1, "应该至少更新一条记录")
        
        # 验证更新后的数据
        with DatabaseSession() as session:
            record = session.query(WipAssy).filter_by(订单号="TEST001").first()
            self.assertEqual(record.研磨, 20, "研磨数量应该被更新")
            self.assertEqual(record.当前工序, "切割", "当前工序应该被更新")

    def test_update_with_invalid_data(self):
        """测试使用无效数据更新"""
        invalid_data = [
            {
                # 缺少订单号
                "封装厂": "池州华宇",
                "研磨": 10
            }
        ]
        
        # 更新供应商进度
        update_stats = self.bll.update_supplier_progress(invalid_data)
        
        # 验证无效数据被正确处理
        self.assertEqual(update_stats['inserted'], 0, "无效数据不应该被插入")

    def test_update_with_empty_data(self):
        """测试使用空数据更新"""
        empty_data = []
        
        # 更新供应商进度
        update_stats = self.bll.update_supplier_progress(empty_data)
        
        # 验证空数据被正确处理
        self.assertEqual(update_stats['inserted'], 0, "空数据不应该被插入")
        self.assertEqual(update_stats['updated'], 0, "空数据不应该更新任何记录")

    def test_update_with_large_numbers(self):
        """测试使用大数值更新"""
        large_number_data = self._create_test_data()
        large_number_data[0]["在线合计"] = 1000000  # 一百万
        
        # 更新供应商进度
        try:
            update_stats = self.bll.update_supplier_progress(large_number_data)
            # 验证更新成功
            self.assertIsInstance(update_stats, dict, "大数值应该能正常更新")
            
            # 验证数据内容
            with DatabaseSession() as session:
                record = session.query(WipAssy).filter_by(订单号="TEST001").first()
                self.assertEqual(record.在线合计, 1000000, "大数值应该正确保存")
        except Exception as e:
            self.fail(f"大数值更新失败: {str(e)}")

    def test_update_with_special_dates(self):
        """测试使用特殊日期更新"""
        special_date_data = self._create_test_data()
        special_date_data[0]["预计交期"] = date(2025, 12, 31)
        
        # 更新供应商进度
        try:
            update_stats = self.bll.update_supplier_progress(special_date_data)
            # 验证更新成功
            with DatabaseSession() as session:
                record = session.query(WipAssy).filter_by(订单号="TEST001").first()
                self.assertEqual(record.预计交期, date(2025, 12, 31), "特殊日期应该正确保存")
        except Exception as e:
            self.fail(f"特殊日期更新失败: {str(e)}")

if __name__ == '__main__':
    unittest.main() 