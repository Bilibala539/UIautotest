"""
测试用例: 退出群组
功能点: 列表操作
操作步骤: 点击单个列表的更多icon → 点击底部菜单的退出群组
预期结果: 点击后有二次弹窗确认和toast反馈，成功后列表不显示该群组
注意: 此操作不可逆，需要有专用测试群
"""
import pytest
from conftest import BaseTest


@pytest.mark.skip(reason="退出群组操作不可逆，需要手动确认专用测试群后再执行")
class TestExitGroup(BaseTest):
    """退出群组"""

    def setup(self):
        self.userA = self.users("userA")

    def test_exit_group(self):
        """
        步骤:
        1. 进入群设置页面
        2. 滑到底部点击"退出群组"
        3. 确认二次弹窗
        4. 验证退出成功
        """
        # 使用测试群号（操作不可逆，谨慎执行）
        self.userA.exit_group("grp.popoqa_test_exit")

    def teardown(self):
        pass
