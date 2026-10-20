# CASE-ID: pay-NEG-025
# LINKED-CASE: M14-NEG-025
"""Swan 回归·M14 支付与会员:订单权益旧屏蔽位空态守门(pay-NEG-025)。

用例 -> AW 映射:
- 「我的」页全域扫查「订单与权益」入口 -> go_bottom_tab("我的") +
  swipe_up 两屏 text_not_exists 扫查(坑 19:旧入口零调用方已下线)
  [OCR]
- 权益组行序断言 -> 权益组完整 4 行名未探索,以「权益中心」行可达承担
  首行语义(完整枚举锚登记 template_needs)
- 深链可达性预标声明 -> order-equity 路由深链考古属执行层,登记 notes

清理:go_home(只读扫查)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayNeg025(BaseTest):
    """订单权益旧屏蔽位空态守门。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_legacy_order_equity_entry_absent(self):
        """我的页全域无「订单与权益」入口,权益中心行可达。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        self.userA.text_not_exists("订单与权益", timeout=5)
        self.userA.swipe_up()
        self.userA.text_not_exists("订单与权益", timeout=5)
        self.userA.open_rights_center()
        self.userA.press_back()
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
