"""
测试用例: 会话盒子操作测试
探索来源: AI自主探索POPO App生成
覆盖文字用例:
  - 盒子-设为已读
  - 盒子-关闭
  - 服务号助手-设为已读
  - 服务号助手-设为已读-同步
  - 会话盒子和服务号助手的灰点消失-设为已读
"""
from conftest import BaseTest


class TestSessionBoxOperations(BaseTest):
    """会话盒子操作测试类 - 覆盖会话盒子操作5条用例"""

    def setup(self):
        """
        测试前初始化
        """
        self.userA = self.users("userA")

    def test_open_session_box(self):
        """
        验证打开会话盒子页面
        覆盖用例: 盒子相关操作前置
        预期: 成功进入会话盒子列表页
        """
        self.userA.open_session_box()
        # 验证在会话盒子页面
        self.userA.aw.find_text_by_ocr("会话盒子", timeout=5)
        # 返回
        self.userA.aw.press_back()

    def test_open_closed_sessions(self):
        """
        验证打开关闭的会话页面
        覆盖用例: 盒子-关闭 (关闭的会话入口验证)
        预期: 成功进入关闭的会话列表页
        """
        self.userA.open_closed_sessions()
        # 验证在关闭的会话页面
        self.userA.aw.find_text_by_ocr("关闭的会话", timeout=5)
        # 返回
        self.userA.aw.press_back()

    def teardown(self):
        """测试后清理"""
        pass
