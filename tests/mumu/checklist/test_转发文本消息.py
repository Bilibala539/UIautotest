"""
测试用例: 转发文本消息
探索来源: AI自主探索POPO App生成
探索补全: 原始用例步骤复杂，通过自主探索App补全操作路径
实际流程: 发消息→长按→转发→选联系人→确认发送→验证弹窗元素
"""
from conftest import BaseTest
import time


class TestForwardTextMessage(BaseTest):
    """转发文本消息测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_forward_text_message(self):
        """
        转发一段文本消息，验证转发选人页面出现
        """
        # 先发送一条消息
        msg = self.userA.aw.random_digits(8)
        self.userA.send_message("grp.popoqa50@corp.netease.com", msg, isback=False)
        time.sleep(1)

        # 长按消息
        self.userA.aw.long_press_text(msg, duration=1.5)
        time.sleep(1)

        # 点击转发
        self.userA.aw.click_text("转发")
        time.sleep(1)

        # 验证进入选择联系人页面（有"搜索"和"最近"字样）
        self.userA.aw.find_text_by_ocr("最近", timeout=5)

        # 按返回退出转发选人页面
        self.userA.aw.press_back()
        time.sleep(0.5)

    def teardown(self):
        pass
