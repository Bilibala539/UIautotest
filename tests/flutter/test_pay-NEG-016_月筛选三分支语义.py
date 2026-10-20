# CASE-ID: pay-NEG-016
# LINKED-CASE: M14-NEG-016
"""Swan 回归·M14 支付与会员:月筛选三分支语义守门(pay-NEG-016)。

用例 -> AW 映射:
- 步骤 1 打开月筛选选定历史月 2026-01 点确认 -> open_month_filter_dialog
  + scroll_wheel_to_value(2026, 1)(2026-01 距当前月 9 格,超出滚轮可视
  窗口,经先下后上逐格 OCR 滚动搜索;坐标全运行时推导)+ confirm_month_filter
  + 入口文案更新断言 assert_month_filter_entry_value(2026, 1)(筛选生效
  的 UI 联动证据;「列表按 2026-01 查询 time 参数」为服务端查询语义,归
  执行层,登记 notes)
- 步骤 2 重开弹层观察重定位+点重置 -> 重开后 OCR 断言当前月值在轮(坑 8
  重定位)+ reset_month_filter + 弹层关闭 + 入口无 2026-01 残留
  assert_month_filter_entry_unset(重置->month=null 的 UI 证据)
- 步骤 3 再设 2025-12 后点关闭(蒙层/返回)-> scroll_wheel_to_value(
  2025, 12) + press_back + 弹层关闭 + 入口无 2025-12 残留(整体 null=
  保持打开前状态的关闭语义,UI 半边=入口无残留;服务端查询语义归执行层)
- 弹层三分支互不混淆由三段生命周期串联承担;滚轮控件/中央选中高亮/
  重置钮细锚登记 template_needs

清理:用例内已还原(关闭分支=null),冷启动模型 teardown pass。
"""
from __future__ import annotations

from datetime import date

from conftest import BaseTest


class TestPayNeg016(BaseTest):
    """月筛选三分支(确认/重置/关闭)语义守门(坑 8)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_month_filter_three_branch_semantics(self):
        """月筛选确认/重置/关闭三分支生命周期互不混淆。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        today = date.today()
        self.userA.open_month_filter_dialog()
        self.userA.scroll_wheel_to_value(2026, 1)
        self.userA.confirm_month_filter()
        self.userA.assert_month_filter_dialog_closed()
        self.userA.assert_month_filter_entry_value(2026, 1)
        self.userA.open_month_filter_dialog()
        items = [i["text"] for i in self.userA.ocr_scan_page()]
        assert any(t in (f"{today.month:02d}", f"{today.month}月")
                   for t in items), "重开后未重定位当前月(坑 8)[OCR]"
        self.userA.reset_month_filter()
        self.userA.assert_month_filter_dialog_closed()
        self.userA.assert_month_filter_entry_unset(2026, 1)
        self.userA.open_month_filter_dialog()
        self.userA.scroll_wheel_to_value(2025, 12)
        self.userA.press_back()
        self.userA.assert_month_filter_dialog_closed()
        self.userA.assert_month_filter_entry_unset(2025, 12)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
