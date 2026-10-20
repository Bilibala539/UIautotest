# CASE-ID: pay-NEG-008
# LINKED-CASE: M14-NEG-008
"""Swan 回归·M14 支付与会员:充值页中途杀 App 守门(pay-NEG-008)。

用例 -> AW 映射:
- 进充值页选中档位(未点支付确认)-> go_bottom_tab("平台") +
  open_recharge_page + select_recharge_tier("¥10");下单请求无流量的
  执行层观察登记 notes
- 杀 App 进程并冷启动 -> relaunch_app(停旧进程+拉起,等价中断链;
  异常日志刷屏观察属执行层)
- 冷启动重进充值记录页 -> ensure_logged_in_on_home(token 持久化)+
  go_bottom_tab("平台") + open_recharge_page + open_recharge_record_page
- 无幽灵待支付订单 -> 前置基线探针(已有待支付单 SKIP-DATA)+
  text_not_exists("待支付")[OCR]

清理:go_home(冷启动后停在记录页,退回首页)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestPayNeg008(BaseTest):
    """充值页中途杀 App 守门(无幽灵订单)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_kill_app_no_phantom_order(self):
        """充值页选档后杀进程冷启动,充值记录页无幽灵待支付订单。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        if self.userA.find_text_by_ocr("待支付", timeout=6) is not None:
            pytest.skip(
                "账号已存在待支付订单,「无幽灵订单」基线不成立(SKIP-DATA)")
        self.userA.press_back()
        self.userA.select_recharge_tier("¥10")
        self.userA.relaunch_app(self.userA.package)
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        self.userA.text_not_exists("待支付", timeout=8)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
