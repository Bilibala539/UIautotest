# CASE-ID: pay-POS-001
# LINKED-CASE: M14-POS-001
"""Swan 回归·M14 支付与会员:充值页经平台页充值入口可达(pay-POS-001)。

用例 -> AW 映射:
- 进入音乐平台页 -> ensure_logged_in_on_home + go_bottom_tab("平台")[图]
- 点击平台页充值入口 -> open_recharge_page 内 click_text("充值")[OCR]
- 充值页加载断言(余额区/六档区/渠道区渲染就绪) -> assert_any_text [OCR]
  (充值页未探索,细锚登记 template_needs)
- 禁区口径:收银台前即止,全程零支付发起(只浏览断言)

清理:go_home(push 页由业务方法内部先退 tab 壳,未发起支付无私有清理)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayPos001(BaseTest):
    """充值页经平台页充值入口可达。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_recharge_page_via_platform_entry(self):
        """平台页充值入口直达充值页,页面区块渲染就绪,零支付发起。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
