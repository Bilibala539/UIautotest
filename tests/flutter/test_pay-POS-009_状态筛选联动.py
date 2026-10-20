# CASE-ID: pay-POS-009
# LINKED-CASE: M14-POS-009
"""Swan 回归·M14 支付与会员:状态筛选弹层六态选择与列表联动(pay-POS-009)。

用例 -> AW 映射:
- 充值段点击状态筛选入口(默认文案「全部」)-> set_record_status_filter
  内 click_text("全部")[OCR]
- 选择「成功」联动列表 -> set_record_status_filter("全部", "成功"),
  入口文案更新断言 [OCR](六选项齐全性/米黄底高亮锚登记 template_needs)
- 恢复筛选为「全部」-> set_record_status_filter("成功", "全部"),入口
  文案回「全部」断言收尾

清理:go_home(筛选已恢复默认,无写操作)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestPayPos009(BaseTest):
    """状态筛选弹层六态选择与列表联动。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_status_filter_select_and_restore(self):
        """状态筛选选「成功」生效,恢复「全部」后入口文案回默认。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        self.userA.set_record_status_filter("全部", "成功")
        self.userA.set_record_status_filter("成功", "全部")
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
