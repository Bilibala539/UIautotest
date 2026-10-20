# CASE-ID: pay-POS-002
# LINKED-CASE: M14-POS-002
"""Swan 回归·M14 支付与会员:充值记录页经充值页记录入口可达(pay-POS-002)。

用例 -> AW 映射:
- 进入充值页 -> go_bottom_tab("平台") + open_recharge_page
  (入口链同 pay-POS-001)[OCR]
- 点击充值页「记录」入口 -> open_recharge_record_page 内
  click_text("记录")[OCR]
- 记录页加载断言(双段切换器可见) -> text_exists("消费")[OCR]
- 普通浏览态,零支付零写操作

清理:go_home(记录页为二级 push,go_home 内部先退 tab 壳)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayPos002(BaseTest):
    """充值记录页经充值页记录入口可达(充值段)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_recharge_record_page_via_recharge_entry(self):
        """充值页「记录」入口直达充值记录页,双段切换器渲染,普通浏览态。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        self.userA.text_exists("消费", timeout=10)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
