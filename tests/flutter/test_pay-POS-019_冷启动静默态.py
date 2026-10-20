# CASE-ID: pay-POS-019
# LINKED-CASE: M14-POS-019
"""Swan 回归·M14 支付与会员:支付协调器就绪静默态(pay-POS-019)。

用例 -> AW 映射:
- 冷启动并完成登录 -> 框架夹具承担冷启动(杀旧进程/拉起/弹窗处置),
  ensure_logged_in_on_home 完成登录与首页壳断言;补单异常弹层/toast 的
  "无"断言由夹具处置+页面锚间接覆盖,形态锚登记 template_needs
- 进入充值页 -> go_bottom_tab("平台") + open_recharge_page,页面正常
  渲染(五值语义细锚登记)
- 退出重进充值记录页 -> press_back + open_recharge_record_page,列表
  稳定(数据去重为服务端语义,UI 以段锚/浏览态覆盖)

清理:go_home。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayPos019(BaseTest):
    """支付协调器就绪静默态(无补单干扰)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_pay_coordinator_silent_ready(self):
        """冷启动登录后进充值页与记录页均正常渲染,退出重进数据稳定。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        self.userA.press_back()
        self.userA.open_recharge_record_page()
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
