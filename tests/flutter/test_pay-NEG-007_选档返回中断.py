# CASE-ID: pay-NEG-007
# LINKED-CASE: M14-NEG-007
"""Swan 回归·M14 支付与会员:选档后返回中断守门(pay-NEG-007)。

用例 -> AW 映射:
- 进充值页选中档位与渠道(不点支付确认)-> go_bottom_tab("平台") +
  open_recharge_page + select_recharge_tier("¥10")(30 元档商品 ID 特例
  对照为执行层数据,登记 notes)
- 系统返回离开充值页 -> press_back 回平台页(assert_any_text 平台页锚
  断言"返回来源页");无确认弹层反断言锚登记 template_needs
- 进充值记录页核对无新增待支付订单 -> 前置先探基线(已有待支付单按
  SKIP-DATA skip),返回后 text_not_exists("待支付")[OCR]

清理:go_home(选档中断零写,未发起支付)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestPayNeg007(BaseTest):
    """选档后返回中断守门(无订单探针)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_tier_select_back_interrupt_zero_write(self):
        """选档后系统返回无确认弹层,充值记录页无新增待支付订单。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        if self.userA.find_text_by_ocr("待支付", timeout=6) is not None:
            pytest.skip(
                "账号已存在待支付订单,「无新增」基线不成立(SKIP-DATA)")
        self.userA.press_back()
        self.userA.select_recharge_tier("¥10")
        self.userA.press_back()
        self.userA.assert_any_text(("总资产", "充值购买"), timeout=10)
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        self.userA.text_not_exists("待支付", timeout=8)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
