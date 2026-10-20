# CASE-ID: pay-POS-010
# LINKED-CASE: M14-POS-010
"""Swan 回归·M14 支付与会员:月筛选弹层定位当前年月与按月确认(pay-POS-010)。

用例 -> AW 映射:
- 充值段点击右上第二筛选入口(月筛选)-> open_month_filter_dialog(入口
  候选探测:月份/当前值前缀)[OCR]
- 断言弹层初始定位为当前年月 -> 弹层 OCR 全量扫描断言当前年/当前月值
  在轮(坑 8 每次打开重定位;中央选中高亮锚登记 template_needs)
- 选择上月并确认 -> select_month_in_wheel(OCR 定位+同列 swipe 步进,
  坐标全运行时)+ confirm_month_filter + 弹层关闭 + 入口文案更新断言
  assert_month_filter_entry_value(上月 yyyy-MM,生效联动证据);列表按
  上月过滤的 time 查询参数为服务端语义,归执行层(细锚登记
  template_needs)
- 数据态:上月/本月各≥1 条订单(YAML TEST-SYNTHETIC 预置),无订单按
  SKIP-DATA skip

清理:重开弹层点「重置」恢复全量。
"""
from __future__ import annotations

from datetime import date

import pytest

from conftest import BaseTest


class TestPayPos010(BaseTest):
    """月筛选弹层定位当前年月与按月确认(坑 8)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_month_filter_dialog_position_and_confirm(self):
        """弹层初始定位当前年月,选上月确认后关闭,重置恢复全量。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        if (self.userA.find_text_by_ocr("¥", timeout=6) is None
                and self.userA.find_text_by_ocr("￥", timeout=3) is None):
            pytest.skip(
                "充值段无预置订单(空态分支,SKIP-DATA):月筛选联动断言跳过")
        today = date.today()
        self.userA.open_month_filter_dialog()
        items = [i["text"] for i in self.userA.ocr_scan_page()]
        assert any(t in (f"{today.month:02d}", f"{today.month}月")
                   for t in items), "弹层未见当前月值(坑 8 定位)[OCR]"
        assert any(today.year in t or t == f"{today.year}年"
                   for t in items), "弹层未见当前年值(坑 8 定位)[OCR]"
        last_month = today.month - 1 or 12
        last_year = today.year - (1 if today.month == 1 else 0)
        self.userA.select_month_in_wheel(last_year, last_month)
        self.userA.confirm_month_filter()
        self.userA.assert_month_filter_dialog_closed()
        self.userA.assert_month_filter_entry_value(last_year, last_month)
        self.userA.open_month_filter_dialog()
        self.userA.reset_month_filter()
        self.userA.assert_month_filter_dialog_closed()
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
