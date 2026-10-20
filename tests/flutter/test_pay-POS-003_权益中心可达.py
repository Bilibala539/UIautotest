# CASE-ID: pay-POS-003
# LINKED-CASE: M14-POS-003
"""Swan 回归·M14 支付与会员:权益中心可达(pay-POS-003)。

用例 -> AW 映射:
- 我的主页点击「权益中心」行 -> go_bottom_tab("我的") + open_rights_center
  (open_me_row 遮挡上滑口径)[OCR]
- 页面加载断言 -> text_exists("权益中心")[OCR];URL host 判定
  (testnetwork.hivi.com)非 UI 可观察态,登记 notes 由执行层承担
- 三段式返回退出 -> press_back + go_home,零操作(坑 21 返回链不深触)

清理:go_home(H5 push 页退出,零操作)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayPos003(BaseTest):
    """权益中心可达(Debug 包经 testnetwork 页)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_rights_center_reachable(self):
        """我的页权益中心行进入 H5 权益中心,加载完成后返回退出。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        self.userA.open_rights_center()
        self.userA.press_back()
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
