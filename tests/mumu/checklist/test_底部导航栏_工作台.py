"""
测试用例: 移动端-下方导航栏-工作台
探索来源: AI自主探索POPO App生成
用例描述: 点击底部工作台Tab，验证可以跳转到工作台页面
"""
from conftest import BaseTest


class TestBottomNavWorkspace(BaseTest):
    """底部导航栏-工作台 测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_navigate_to_workspace(self):
        """
        点击底部导航栏工作台，验证可跳转到工作台页面
        """
        # 点击底部工作台Tab
        self.userA.click_text("工作台")
        import time
        time.sleep(2)

        # 验证已进入工作台页面 - 页面显示"我的应用"和"远程办公"
        self.userA.text_exists("我的应用", timeout=10)

    def teardown(self):
        pass
