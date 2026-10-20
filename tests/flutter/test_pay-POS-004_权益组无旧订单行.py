# CASE-ID: pay-POS-004
# LINKED-CASE: M14-POS-004
"""Swan 回归·M14 支付与会员:订单权益旧入口屏蔽位迁移确认(pay-POS-004)。

用例 -> AW 映射:
- 我的主页遍历我的权益组行集合 -> go_bottom_tab("我的") + swipe_up 两屏
  扫查(权益组完整 4 行名未探索,枚举锚登记 template_needs)
- 断言无「订单与权益」旧行 -> text_not_exists [OCR](坑 19 零调用方)
- 权益中心行作为现行可达入口 -> open_rights_center 进入断言

清理:go_home(只读扫查)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayPos004(BaseTest):
    """订单权益旧入口屏蔽位迁移确认(权益中心取代)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_legacy_order_equity_row_removed(self):
        """我的页全域无「订单与权益」旧行,权益中心行存在且可进入。"""
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
