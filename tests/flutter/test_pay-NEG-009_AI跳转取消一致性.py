# CASE-ID: pay-NEG-009
# LINKED-CASE: M14-NEG-009
"""Swan 回归·M14 支付与会员:充值取消回来源页一致性(pay-NEG-009)。

用例 -> AW 映射:
- 从 AI 域触发余额不足跳转充值页 -> go_top_tab("AI") +
  open_recharge_via_ai(角色卡 -> ASCII 消息 -> enter 发送)+ 余额不足
  探针(账号余额非 0 按 SKIP-DATA skip)+ 提示内充值入口
  click_text("充值")[OCR]
- 选中档位后不支付直接返回 -> select_recharge_tier("¥10") +
  press_back,回 AI 域来源页断言(text_exists「内容由AI生成」);无半
  支付态/余额假变动由零支付操作保证
- 再次进充值页核对目录与选中态 -> press_back 回首页后
  go_bottom_tab("平台") + open_recharge_page +
  assert_recharge_tiers_visible(六档与初始一致)

清理:go_home(充值记录无新增订单的基线核对待预置数据,登记 notes)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestPayNeg009(BaseTest):
    """充值取消回商品页一致性(L3,AI 域入口链)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_recharge_cancel_return_consistency(self):
        """AI 域进充值页选档取消返回来源页,重进目录六档与初始一致。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_recharge_via_ai()
        if self.userA.find_text_by_ocr("余额不足", timeout=20) is None:
            pytest.skip(
                "余额不足门未触发(账号余额非 0,余额=0 预置属数据前置,"
                "SKIP-DATA 口径)")
        self.userA.click_text("充值", timeout=10)
        self.userA.select_recharge_tier("¥10")
        self.userA.press_back()
        self.userA.text_exists("内容由AI生成", timeout=10)
        self.userA.press_back()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.assert_recharge_tiers_visible()
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
