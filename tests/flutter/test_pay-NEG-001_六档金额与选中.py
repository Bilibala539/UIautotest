# CASE-ID: pay-NEG-001
# LINKED-CASE: M14-NEG-001
"""Swan 回归·M14 支付与会员:金额缩放安全门 UI 侧守门(pay-NEG-001)。

用例 -> AW 映射:
- 步骤 1 执行层检查金额缩放开关编译期常量 -> 非 UI 步骤(源码/包静态
  检查),不在 UI 自动化口径内,由执行层承担(report notes 已登记)
- 进充值页核对六档金额展示 -> go_bottom_tab("平台") + open_recharge_page
  + assert_recharge_tiers_visible(六档 ¥10/¥20/¥30/¥60/¥100/¥200,
  ¥/￥ OCR 变体兼容)[OCR]
- 选中任一档观察(不点支付)-> select_recharge_tier("¥10"),商品 ID
  展示锚登记 template_needs;误开缩放时金额=元/1000 的篡改由六档文案
  断言拦截

清理:go_home(未发起支付)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayNeg001(BaseTest):
    """金额缩放开关前置守门(UI 侧六档一致性)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_recharge_tiers_consistent(self):
        """充值页六档金额与目录常量一致,选中档位本地态正常,零支付。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.assert_recharge_tiers_visible()
        self.userA.select_recharge_tier("¥10")
        self.userA.press_back()
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
