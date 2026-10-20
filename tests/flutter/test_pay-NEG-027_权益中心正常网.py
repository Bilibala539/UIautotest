# CASE-ID: pay-NEG-027
# LINKED-CASE: M14-NEG-027
"""Swan 回归·M14 支付与会员:权益中心会员面 UI 侧守门(pay-NEG-027)。

用例 -> AW 映射:
- 正常网进权益中心记录惠威币余额展示 -> go_bottom_tab("我的") +
  open_rights_center(标题锚
  即装载判据;余额展示与充值页同源的具体数值断言依赖 H5 首屏文案锚,
  登记 template_needs)[OCR]
- 断网重进权益中心 watchdog 重试面板 -> 需执行层断网能力,登记
  skipped 语义由 pay-NEG 域断网族统一承担(见 report notes)
- H5 消费侧边界声明 -> H5 行为 App 仓不可见,执行层口径

清理:go_home(正常网页面只读)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayNeg027(BaseTest):
    """权益中心会员面断网守门(UI 侧正常网半边)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_rights_center_online_baseline(self):
        """正常网进权益中心装载完成,可返回退出(H5 基线对照半边)。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        self.userA.open_rights_center()
        self.userA.press_back()
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
