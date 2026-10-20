# CASE-ID: help-POS-001
# LINKED-CASE: M15-POS-001
"""Swan 回归·M15 帮助与反馈:帮助入口页可达且固定 4 行渲染(help-POS-001)。

用例 -> AW 映射:
- 登录态进我的页 -> ensure_logged_in_on_home + go_bottom_tab("我的")[图]
- 点击「帮助与反馈」入口行 -> open_help_feedback_page(open_me_row 遮挡
  上滑口径)[OCR]
- 固定 4 行自上而下顺序 -> assert_help_rows_in_order(型号/使用说明/
  用户反馈/常见问题,y 序严格递增)[OCR]
- 「用户反馈」行红点容器 -> 无未读数时不可见属预期,不作断言门槛

清理:go_home(入口页只读浏览)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestHelpPos001(BaseTest):
    """帮助与反馈入口页可达且固定 4 行渲染。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_help_feedback_entry_four_rows(self):
        """帮助入口页打开,固定 4 行按序渲染完整。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        self.userA.open_help_feedback_page()
        self.userA.assert_help_rows_in_order()
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
