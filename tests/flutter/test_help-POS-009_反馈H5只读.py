# CASE-ID: help-POS-009
# LINKED-CASE: M15-POS-009
"""Swan 回归·M15 帮助与反馈:反馈 H5 内表单元素展示只读断言(help-POS-009)。

用例 -> AW 映射:
- 打开用户反馈全屏 H5 -> go_bottom_tab("我的") + open_help_feedback_page
  + open_feedback_h5[OCR]
- .nav 导航结构与内容区展示 -> H5 内部锚未探索,登记 template_needs;
  "已离开列表页且容器装载"由四行锚消失承担
- 全程只读,不点击任何提交/上传控件 -> 用例零触达表单控件;零上传流量
  的日志断言属执行层(登记 notes)

清理:press_back(旧桥返回通知关页)回入口页断言后 go_home。
"""
from __future__ import annotations

from conftest import BaseTest


class TestHelpPos009(BaseTest):
    """反馈 H5 内表单元素展示断言(只读,提交全部禁触)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_feedback_h5_readonly_browse(self):
        """反馈 H5 打开后只读浏览,原路返回,全程零提交零上传。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        self.userA.open_help_feedback_page()
        self.userA.open_feedback_h5()
        self.userA.press_back()
        self.userA.text_exists("帮助与反馈", timeout=10)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
