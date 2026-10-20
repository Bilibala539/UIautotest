# CASE-ID: help-POS-003
# LINKED-CASE: M15-POS-003
"""Swan 回归·M15 帮助与反馈:使用说明入口打开 H5(help-POS-003)。

用例 -> AW 映射:
- 帮助入口页点击「使用说明」行 -> go_bottom_tab("我的") +
  open_help_feedback_page + click_text("使用说明")[OCR]
- H5 装载完成(非白屏)-> newadmin H5 首屏文案未探索,以帮助入口页
  四行锚消失承担"已离开"判据,细锚登记 template_needs
- rootBackHook 注入日志/H5 顶栏返回(.back-button)-> 日志探针与 H5
  内部锚未探索,登记 notes/template_needs;返回以系统返回键等效承担

清理:press_back 回入口页断言后 go_home。
"""
from __future__ import annotations

from conftest import BaseTest


class TestHelpPos003(BaseTest):
    """使用说明入口打开 H5(newadmin)且返回钩子就绪。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_usage_guide_h5_open(self):
        """使用说明行进入 H5,系统返回回帮助入口页,无崩溃。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        self.userA.open_help_feedback_page()
        self.userA.click_text("使用说明", timeout=10)
        self.userA.text_not_exists("可适配音箱型号", timeout=10)
        self.userA.press_back()
        self.userA.text_exists("帮助与反馈", timeout=10)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
