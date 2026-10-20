# CASE-ID: pay-NEG-017
# LINKED-CASE: M14-NEG-017
"""Swan 回归·M14 支付与会员:记录详情深链无数据源守门(pay-NEG-017,部分转换)。

用例 -> AW 映射(部分转换:步骤 1/3 正常路径先行,步骤 2 归执行层):
- 步骤 1 正常路径进详情页(列表行点击)-> open_record_detail_first_row
  (详情数据=列表内存缓存无 HTTP 为日志侧语义,登记 notes 由执行层承担)
- 步骤 2 深链直达 /me/recharge-record/detail -> YAML 预标 BLOCKED
  (通道未考古),需路由深链注入通道(框架缺口),登记 notes 由专用轮
  承担;UI 自动化不覆盖
- 步骤 3 详情页按系统返回 -> press_back + text_exists("消费") 回记录页
  (坑 9 PopScope 接管关闭的 UI 可观察半边)
- 数据态:≥1 条历史订单,不足按 SKIP-DATA skip

清理:无(只读断言)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestPayNeg017(BaseTest):
    """记录详情正常路径与返回接管守门(深链步骤断言归执行层)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_record_detail_back_takeover(self):
        """正常路径进详情后系统返回由页面接管关闭,回记录页无崩溃。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        if (self.userA.find_text_by_ocr("¥", timeout=6) is None
                and self.userA.find_text_by_ocr("￥", timeout=3) is None):
            pytest.skip(
                "充值段无预置订单(空态分支,SKIP-DATA):详情页断言跳过")
        self.userA.open_record_detail_first_row()
        self.userA.press_back()
        self.userA.text_exists("消费", timeout=10)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
