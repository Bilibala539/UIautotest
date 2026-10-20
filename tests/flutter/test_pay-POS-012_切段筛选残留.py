# CASE-ID: pay-POS-012
# LINKED-CASE: M14-POS-012
"""Swan 回归·M14 支付与会员:消费明细段浏览与切段筛选残留(pay-POS-012)。

用例 -> AW 映射:
- 充值段设状态筛选=「成功」基线 -> set_record_status_filter("全部",
  "成功")[OCR]
- 切换至「消费」段 -> click_text("消费") + text_exists("消费")[OCR];
  月份被清/状态入口不可见细断言依赖段切换器与月份入口 region 模板
  (登记 template_needs)
- 切回「充值」段状态仍生效 -> click_text("充值") 后经筛选入口恢复
  「全部」(入口文案=「成功」即残留生效的可达证据)
- 恢复筛选默认收尾

清理:go_home(筛选已恢复)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayPos012(BaseTest):
    """消费明细段浏览与切段筛选残留语义(清月份保状态)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_segment_switch_filter_residual(self):
        """充值段设「成功」后切消费段再切回,状态筛选保留生效并恢复默认。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        self.userA.set_record_status_filter("全部", "成功")
        self.userA.click_text("消费", timeout=8)
        self.userA.text_exists("消费", timeout=8)
        self.userA.click_text("充值", timeout=8)
        self.userA.set_record_status_filter("成功", "全部")
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
