# CASE-ID: pay-POS-006
# LINKED-CASE: M14-POS-006
"""Swan 回归·M14 支付与会员:充值页渠道列表与缺省映射(pay-POS-006)。

用例 -> AW 映射:
- 进入充值页断言渠道区渲染 -> go_bottom_tab("平台") + open_recharge_page
  + text_exists [OCR]
  (Android 缺省渠道=微信+支付宝,availableChannels 口径)
- 渠道可用性形态(已装可用/未装不可用)依赖设备安装态,细锚登记
  template_needs
- 不发起任何支付,返回:全程只读断言,禁触收银台(禁区 1)

清理:go_home(未拉起收银台)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayPos006(BaseTest):
    """充值页渠道列表与缺省映射(微信+支付宝)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_channel_list_default_mapping(self):
        """充值页渠道区渲染微信+支付宝两项,全程未拉起收银台。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.text_exists("微信", timeout=10)
        self.userA.text_exists("支付宝", timeout=10)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
