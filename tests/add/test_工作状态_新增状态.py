"""
测试用例: 工作状态-新增状态成功
功能点: 在工作状态设置页面新增自定义状态
操作步骤: 1.输入正确的状态名称 2.选择状态icon 3.点击保存
预期结果: 1.弹出toast"状态新增成功" 2.返回工作状态设置页面，新增的状态显示在列表底部
"""
import time
import pytest
from conftest import BaseTest


@pytest.mark.skip(reason="工作状态入口随当前状态变化(有状态→显示状态名;无状态→显示'+工作状态'按钮)，需探索稳定入口")
class TestWorkStatusAdd(BaseTest):
    """工作状态-新增状态"""

    def setup(self):
        self.userA = self.users("userA")

    def test_add_custom_work_status(self):
        """需要探索: 工作状态新增流程"""
        pass

    def teardown(self):
        pass
