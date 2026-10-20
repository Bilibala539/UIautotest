# CASE-ID: pay-POS-005
# LINKED-CASE: M14-POS-005
"""Swan 回归·M14 支付与会员:充值页六档静态展示与选中态(pay-POS-005)。

用例 -> AW 映射:
- 进入充值页 -> go_bottom_tab("平台") + open_recharge_page
  (入口链同 pay-POS-001)[OCR]
- 六档商品全部渲染 -> assert_recharge_tiers_visible(¥/￥ OCR 变体兼容)
- 点击选中 ¥30 档 -> select_recharge_tier("¥30")(选中态视觉锚登记
  template_needs;本地选中不发起收银台)
- 返回退出充值页 -> press_back 后 go_home,无支付进行中残留即无异常

清理:go_home(未发起任何支付)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayPos005(BaseTest):
    """充值页商品目录六档静态展示(选中态)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_recharge_tiers_render_and_select(self):
        """充值页六档全部渲染,选中 ¥30 档无收银台,返回退出无异常。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.assert_recharge_tiers_visible()
        self.userA.select_recharge_tier("¥30")
        self.userA.press_back()
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
