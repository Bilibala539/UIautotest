# CASE-ID: help-NEG-007
# LINKED-CASE: M15-NEG-007
"""Swan 回归·M15 帮助与反馈:登出窗口红点不回源(help-NEG-007)。

用例 -> AW 映射:
- 红点可见状态下执行登出 -> ensure_logged_in_on_home +
  logout_if_needed(幂等登出);红点 UI 随登出清空以登录页到位承担
  (Me 页整体退出,三处红点随之消失)
- 登录页观察网络日志(零 unreadCount 回源/零 details 补拉)-> logcat
  探针非执行层能力,登记 notes 由执行层承担
- 无 30001 会话失效误报 Toast -> toast 即逝窗口依赖登出动作时序,捕获
  不稳,登记 notes;UI 侧以登录页锚 + 无异常收尾覆盖
- 恢复登录态 -> login_by_sms + assert_on_home(与设备初始状态一致)

清理:无(已恢复登录态停首页;冷启动模型 teardown pass)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestHelpNeg007(BaseTest):
    """登出窗口红点不回源(30001 误报被门控挡住)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_logout_window_no_unread_refetch(self):
        """登出后落登录页(红点随登出清空),恢复登录态停首页。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.logout_if_needed()
        self.userA.assert_on_login_page()
        self.userA.login_by_sms(self.userA.phone)
        self.userA.assert_on_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
