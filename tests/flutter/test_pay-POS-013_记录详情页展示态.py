# CASE-ID: pay-POS-013
# LINKED-CASE: M14-POS-013
"""Swan 回归·M14 支付与会员:充值记录详情页展示态(pay-POS-013)。

用例 -> AW 映射:
- 充值段列表记录首行要素(金额/时间/状态)-> scan_record_rows OCR 行
  聚类记录首行键[OCR]
- 点击首行进入详情页 -> open_record_detail_first_row(push detail 到位
  判据=段切换器「消费」锚消失;详情==行要素的一致性比对依赖详情页首屏
  锚,登记 template_needs;坑 5 详情=列表内存缓存无 HTTP,HTTP 半边
  登记 notes)
- 按系统返回键退出详情 -> press_back + text_exists("消费") 回记录页
  (坑 9 PopScope 接管关闭的 UI 可观察半边)
- 数据态:服务端预置≥1 条历史充值订单,不足按 SKIP-DATA skip

清理:无(只读浏览)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestPayPos013(BaseTest):
    """充值记录详情页展示态(缓存一致+清栈返回)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_record_detail_display_and_back(self):
        """首行进详情页,系统返回回记录页,只读浏览零写操作。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        if (self.userA.find_text_by_ocr("¥", timeout=6) is None
                and self.userA.find_text_by_ocr("￥", timeout=3) is None):
            pytest.skip(
                "充值段无预置订单(空态分支,SKIP-DATA):详情页断言跳过")
        first_key = self.userA.open_record_detail_first_row()
        assert first_key, "首行行键为空(OCR 聚类异常)"
        self.userA.press_back()
        self.userA.text_exists("消费", timeout=10)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
