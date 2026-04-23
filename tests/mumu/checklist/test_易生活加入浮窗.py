"""
测试用例: 易生活加入浮窗
探索来源: AI自主探索POPO App生成
探索补全: 底部导航栏→易生活→右上角更多→浮窗
"""
from conftest import BaseTest


class TestElifeFloatingWindow(BaseTest):
    """易生活加入浮窗功能测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_add_elife_to_floating_window(self):
        """
        测试易生活加入浮窗功能

        步骤:
        1. 从消息列表页点击底部Tab"易生活"
        2. 处理地理位置权限弹窗（如出现）
        3. 点击右上角"..."更多按钮
        4. 在弹出菜单中点击"浮窗"
        5. 验证操作完成（菜单关闭，回到易生活页面）
        6. 返回消息列表页
        """
        self.userA.add_elife_to_floating_window()

    def teardown(self):
        pass
