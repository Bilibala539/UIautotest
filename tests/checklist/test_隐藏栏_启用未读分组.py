"""
测试用例: 隐藏栏-启用未读分组
探索来源: AI自主探索POPO App
用例描述: 在管理分组页面，将隐藏的分组启用（点击+号），验证分组移到展示区域
ODS用例: 隐藏栏-启用未读分组
"""
import time
from conftest import BaseTest


class TestEnableHiddenSessionGroup(BaseTest):
    """隐藏栏-启用分组 测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_enable_hidden_session_group(self):
        """
        步骤:
        1. 进入管理分组页面
        2. 滚动到隐藏区域
        3. 点击隐藏分组前的+号，启用该分组
        4. 验证分组从隐藏栏移动到启用栏
        """
        # 启用隐藏的"群组"分组
        result = self.userA.enable_hidden_session_group("群组")
        assert result, "启用隐藏分组应该成功"

    def teardown(self):
        """清理：将启用的分组重新隐藏"""
        try:
            self.userA.disable_session_group("群组")
        except Exception:
            pass
