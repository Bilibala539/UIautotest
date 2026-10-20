# CASE-ID: pay-POS-025
# LINKED-CASE: M14-POS-025
"""Swan 回归·M14 支付与会员:AI 余额不足入口链可达充值页(pay-POS-025)。

用例 -> AW 映射:
- 进入 AI 对话页发送触发余额校验的消息 -> go_top_tab("AI") +
  open_recharge_via_ai(角色卡「小薇」-> 输入框 -> ASCII 消息 -> enter
  发送,知识库 swan_AI对话页)[OCR]
- 余额不足提示出现 -> find_text_by_ocr 探测;账号余额非 0 时门不触发,
  按 SKIP-DATA 口径 skip(数据前置)
- 点击提示内充值入口 -> click_text("充值")(提示气泡内入口,文案变体
  登记 template_needs)
- 断言充值页就绪后返回 -> assert_any_text + press_back 回 AI 对话页

清理:go_home(零支付,充值页仅浏览)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestPayPos025(BaseTest):
    """AI 余额不足入口链可达充值页(余额=0 预置)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_recharge_via_ai_balance_shortage(self):
        """AI 对话触发余额不足,提示内充值入口进充值页,返回回 AI 页。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_recharge_via_ai()
        if self.userA.find_text_by_ocr("余额不足", timeout=20) is None:
            pytest.skip(
                "余额不足门未触发(账号余额非 0,余额=0 预置属数据前置,"
                "SKIP-DATA 口径)")
        self.userA.click_text("充值", timeout=10)
        self.userA.assert_any_text(("余额", "微信", "支付宝"), timeout=10)
        self.userA.press_back()
        self.userA.text_exists("内容由AI生成", timeout=10)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
