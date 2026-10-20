# CASE-ID: help-POS-004
# LINKED-CASE: M15-POS-004
"""Swan 回归·M15 帮助与反馈:常见问题入口打开 H5(help-POS-004)。

用例 -> AW 映射:
- 帮助入口页点击「常见问题」行 -> go_bottom_tab("我的") +
  open_help_feedback_page + click_text("常见问题")[OCR]
- H5 装载完成(privacy/faq.html 非白屏)-> faq H5 首屏文案未探索,以
  帮助入口页四行锚消失承担"已离开"判据,细锚登记 template_needs
- 捏合缩放锁定断言 -> 多点触控手势框架无此能力,缩放锁定现状登记
  notes 由专项轮承担;本用例承担装载+返回链

清理:press_back 回入口页断言后 go_home。
"""
from __future__ import annotations

from conftest import BaseTest


class TestHelpPos004(BaseTest):
    """常见问题入口打开 H5(faq)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_faq_h5_open(self):
        """常见问题行进入 H5,系统返回回帮助入口页,无崩溃。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        self.userA.open_help_feedback_page()
        self.userA.click_text("常见问题", timeout=10)
        self.userA.text_not_exists("可适配音箱型号", timeout=10)
        self.userA.press_back()
        self.userA.text_exists("帮助与反馈", timeout=10)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
