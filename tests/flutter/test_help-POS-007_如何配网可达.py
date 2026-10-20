# CASE-ID: help-POS-007
# LINKED-CASE: M15-POS-007
"""Swan 回归·M15 帮助与反馈:如何配网页经添加设备页入口可达(help-POS-007)。

用例 -> AW 映射:
- 进入添加设备页点击「如何配网」入口 -> open_device_page 设备页 [图] +
  open_how_to_connect_page(「添加设备」->「如何配网」[OCR];
  添加设备入口文案变体登记 template_needs)
- 配网 H5 装载 -> 首屏文案未探索,登记 template_needs
- 点击顶栏「可适配音箱型号」动作入口 -> click_text 进入 speaker-models
  H5,以「如何配网」锚消失承担已跳转判据

清理:go_home(H5 push 链由业务方法内部退 tab 壳)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestHelpPos007(BaseTest):
    """如何配网页经添加设备页入口可达且顶栏入口可用。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_how_to_connect_reachable(self):
        """添加设备页「如何配网」进配网页,顶栏型号动作入口可点可达。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        self.userA.open_how_to_connect_page()
        self.userA.click_text("可适配音箱型号", timeout=10)
        self.userA.text_not_exists("如何配网", timeout=10)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
