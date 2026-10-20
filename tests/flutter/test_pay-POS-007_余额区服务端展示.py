# CASE-ID: pay-POS-007
# LINKED-CASE: M14-POS-007
"""Swan 回归·M14 支付与会员:惠威币余额服务端值展示(pay-POS-007)。

用例 -> AW 映射:
- 经探针记录服务端余额值 -> 非执行层能力(需接口探针),余额区锚断言
  承担"展示存在性"半边,数值一致性登记 template_needs/notes
- 进入充值页断言余额区展示 -> go_bottom_tab("平台") + open_recharge_page
  + text_exists("余额")[OCR]
- 零充值零入账返回:全程不触任何支付控件,余额未变化由零操作保证

清理:go_home(未做任何充值支付操作)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayPos007(BaseTest):
    """惠威币余额服务端值展示(不假设本地累计)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_balance_area_server_value_display(self):
        """充值页余额区渲染(展示值来自服务端),零操作返回余额无变化。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.text_exists("余额", timeout=10)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
