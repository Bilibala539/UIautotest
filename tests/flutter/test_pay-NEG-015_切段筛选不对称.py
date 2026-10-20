# CASE-ID: pay-NEG-015
# LINKED-CASE: M14-NEG-015
"""Swan 回归·M14 支付与会员:切段筛选残留不对称守门(pay-NEG-015)。

用例 -> AW 映射:
- 充值段设状态筛选「失败」+月份筛选 -> set_record_status_filter(
  "全部", "失败");月份筛选为滚轮控件,选定历史月依赖滚轮锚(登记
  template_needs,本用例以状态残留主链承担坑 7 核心语义)[OCR]
- 切到消费段 -> click_text("消费") + text_exists("消费");月份被清/
  状态入口不可见细断言依赖段切换器 region 模板(登记 template_needs)
- 切回充值段 -> click_text("充值"),状态筛选「失败」仍生效 -> 经筛选
  入口恢复「全部」(入口文案=「失败」即残留生效的可达证据)

清理:go_home(筛选已恢复默认)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayNeg015(BaseTest):
    """切段筛选残留不对称守门(坑 7,清月份保状态)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_segment_switch_asymmetric_residual(self):
        """充值段设「失败」切消费段再切回,状态筛选残留生效后恢复默认。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        self.userA.set_record_status_filter("全部", "失败")
        self.userA.click_text("消费", timeout=8)
        self.userA.text_exists("消费", timeout=8)
        self.userA.click_text("充值", timeout=8)
        self.userA.set_record_status_filter("失败", "全部")
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
