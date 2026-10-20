# CASE-ID: pay-NEG-004
# LINKED-CASE: M14-NEG-004
"""Swan 回归·M14 支付与会员:充值页进入副作用守门 UI 侧(pay-NEG-004)。

用例 -> AW 映射:
- 进充值页记录网络副作用/补单弹层形态 -> 网络流量与日志观察非执行层
  能力,登记 notes;进入即副作用(StoreKit 预取/补单扫描)按坑 10 口径
  记录环境事实不判失败,弹窗由框架夹具统一处置
- 快速进出充值页 3 次 -> go_bottom_tab("平台") 后循环 open_recharge_page
  + press_back,每轮页面锚断言(副作用不叠加/无崩溃的 UI 可观察面)
- 无多重弹层 -> 每轮到位断言兜底(弹层残留会阻塞锚点命中)

清理:go_home(未发起支付)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayNeg004(BaseTest):
    """充值页进入即副作用守门(坑 10,快速进出 3 次)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_recharge_page_repeated_enter_exit(self):
        """快速进出充值页 3 次,每轮渲染就绪,副作用不叠加无崩溃。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        for _ in range(3):
            self.userA.open_recharge_page()
            self.userA.press_back()
        self.userA.open_recharge_page()
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
