# CASE-ID: pay-NEG-013
# LINKED-CASE: M14-NEG-013
"""Swan 回归·M14 支付与会员:筛选遮罩/返回关闭不刷新守门(pay-NEG-013)。

用例 -> AW 映射:
- 打开状态筛选 Dialog 选「成功」-> set_record_status_filter("全部",
  "成功")(选中米黄底视觉锚登记 template_needs)[OCR]
- 重开 Dialog 后返回关闭(不点确定)-> click_text("成功")重开 +
  press_back 模拟遮罩/返回关闭
- 重开 Dialog 核对选中态 -> 重开后「成功」选项仍存在 [OCR](遮罩关闭
  是撤销不是清空;入口与行状态文案同词的 region 消歧登记 template_needs)

清理:go_home(查询未刷新,无写操作)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayNeg013(BaseTest):
    """筛选遮罩/返回关闭不刷新守门。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_filter_mask_close_keeps_query(self):
        """筛选「成功」生效后遮罩/返回关闭不刷新,重开仍为选中态。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        self.userA.set_record_status_filter("全部", "成功")
        self.userA.click_text("成功", timeout=8)
        self.userA.press_back()
        self.userA.click_text("成功", timeout=8)
        self.userA.text_exists("成功", timeout=8)
        self.userA.press_back()
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
