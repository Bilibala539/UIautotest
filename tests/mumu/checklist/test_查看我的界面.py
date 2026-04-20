"""
测试用例: 查看我的界面
探索来源: AI自主探索POPO App生成
用例描述: 点击"我的"进入界面查看，验证侧边栏界面正常显示
"""
from conftest import BaseTest


class TestViewMyInterface(BaseTest):
    """查看我的界面 测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_view_my_interface(self):
        """
        点击左上角头像进入侧边栏（我的界面），验证界面元素正常显示
        """
        # 打开侧边栏（POPO的"我的"入口是侧边栏）
        self.userA.open_sidebar()

        # 验证侧边栏关键元素存在
        self.userA.text_exists("我的收藏")
        self.userA.text_exists("设置")

        # 返回消息列表
        self.userA.aw.press_back()

    def teardown(self):
        pass
