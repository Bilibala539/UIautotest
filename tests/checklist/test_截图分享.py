"""
测试用例: 截图分享
探索来源: AI自主探索POPO App生成
探索补全: 系统截图→POPO检测截图→分享截图→选人→发送
"""
from conftest import BaseTest


class TestScreenshotAndShare(BaseTest):
    """截图分享功能测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_screenshot_and_share(self):
        """
        测试系统截图后通过POPO分享功能

        步骤:
        1. 进入 grp.popoqa50 聊天页面
        2. 触发系统截图 (KEYCODE_SYSRQ)
        3. POPO弹出"分享截图"提示，点击进入选人页面
        4. 选择 grp.popoqa50 发送截图
        5. 验证发送成功
        6. 返回消息列表
        """
        self.userA.screenshot_and_share(recipient="grp.popoqa50")

    def teardown(self):
        pass
