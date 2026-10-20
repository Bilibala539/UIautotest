# CASE-ID: pay-NEG-005
# LINKED-CASE: M14-NEG-005
"""Swan 回归·M14 支付与会员:渠道列表过滤与缺省映射守门 UI 侧(pay-NEG-005)。

用例 -> AW 映射:
- 进充值页观察渠道列表 -> go_bottom_tab("平台") + open_recharge_page
  + text_exists("微信")/
  text_exists("支付宝")[OCR](Android 缺省 availableChannels=微信+
  支付宝,digital 协议 1/2)
- 代理注入未知渠道值/IAP 退款面断言 -> 需代理注入与 IAP 订单数据,
  非执行层能力,登记 notes 由执行层承担
- 全程只读断言,不发起任何支付(禁区 1)

清理:go_home。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayNeg005(BaseTest):
    """渠道列表过滤与缺省映射守门(UI 侧缺省面)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_channel_list_default_filter(self):
        """充值页渠道面与 Android 缺省一致(微信+支付宝),只读断言。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.text_exists("微信", timeout=10)
        self.userA.text_exists("支付宝", timeout=10)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
