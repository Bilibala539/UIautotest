"""
测试用例: 跳转会话盒子详情页
功能点: 新增会话分组模块
操作步骤: 分组栏展开后，点击会话盒子
预期结果: 跳转到会话盒子列表页
"""
from conftest import BaseTest


class TestOpenSessionBoxDetail(BaseTest):
    """跳转会话盒子详情页"""

    def setup(self):
        self.userA = self.users("userA")

    def test_open_session_box_detail(self):
        """
        步骤:
        1. 打开分组面板（点击"展开"）
        2. 点击"会话盒子"标签
        3. 验证进入会话盒子详情页
        """
        self.userA.open_session_group_panel()
        self.userA.open_session_box_detail()

    def teardown(self):
        """返回消息列表"""
        self.userA.aw.press_back()
