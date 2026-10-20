# CASE-ID: help-POS-008
# LINKED-CASE: M15-POS-008
"""Swan 回归·M15 帮助与反馈:用户反馈入口打开全屏 H5(help-POS-008)。

用例 -> AW 映射:
- 帮助入口页点击「用户反馈」行 -> go_bottom_tab("我的") +
  open_help_feedback_page + open_feedback_h5(click_text + 四行锚消失
  判据)[OCR]
- query 四参数断言(userId/appVersion/telType/telVersion)-> URL/日志
  侧断言非执行层能力,登记 notes 由执行层承担
- H5 页面标题断言 -> 反馈 H5 首屏文案未探索,登记 template_needs;
  全屏容器形态由四行锚消失(无标题栏 push 覆盖)承担

清理:press_back 回入口页断言后 go_home。
"""
from __future__ import annotations

from conftest import BaseTest


class TestHelpPos008(BaseTest):
    """用户反馈入口打开全屏 H5(query 四参数由执行层核对)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_feedback_h5_fullscreen_open(self):
        """用户反馈行进入全屏 H5,返回回帮助入口页,无崩溃。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        self.userA.open_help_feedback_page()
        self.userA.open_feedback_h5()
        self.userA.press_back()
        self.userA.text_exists("帮助与反馈", timeout=10)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
