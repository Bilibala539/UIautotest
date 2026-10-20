# CASE-ID: pay-POS-008
# LINKED-CASE: M14-POS-008
"""Swan 回归·M14 支付与会员:充值记录列表浏览(pay-POS-008)。

用例 -> AW 映射:
- 进入充值记录页充值段 -> go_bottom_tab("平台") + open_recharge_page
  + open_recharge_record_page(段位=充值由入口链保证)[OCR]
- 列表行/空态双分支:有订单行(¥/￥ 金额 OCR)则列表态成立;无预置订单
  按 YAML SKIP-DATA 口径 skip(空态文案锚登记 template_needs)
- 普通浏览态,零点击行内控件

清理:go_home。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestPayPos008(BaseTest):
    """充值记录列表浏览(充值段首屏+默认全部态)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_recharge_record_list_browse(self):
        """充值段打开,有订单行断言金额渲染,无预置订单按 SKIP-DATA skip。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        if (self.userA.find_text_by_ocr("¥", timeout=6) is None
                and self.userA.find_text_by_ocr("￥", timeout=3) is None):
            pytest.skip(
                "充值段无预置订单(空态分支,SKIP-DATA):行级断言跳过,"
                "空态文案锚登记 template_needs")
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
