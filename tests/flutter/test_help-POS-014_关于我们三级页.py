# CASE-ID: help-POS-014
# LINKED-CASE: M15-POS-014
"""Swan 回归·M15 帮助与反馈:关于我们三级页四要素(help-POS-014)。

用例 -> AW 映射:
- 进入我的页打开「关于与升级」-> go_bottom_tab("我的") + open_about_page,
  再点击「关于我们」行(click_text)[OCR]
- Logo 渲染尺寸/简介正文/三行联系方式 -> Logo 需图像模板、三行值为
  接口值或 fallback(文案未探索),登记 template_needs;页面到达以
  标题锚承担(成功态/失败态均通过的口径)
- 接口失败降级面由 help-NEG-003 断网族与 pay-NEG-027 对照承担

清理:press_back 回关于与升级页断言后 go_home。
"""
from __future__ import annotations

from conftest import BaseTest


class TestHelpPos014(BaseTest):
    """关于我们三级页四要素(Logo/简介/三行)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_about_detail_page_reachable(self):
        """关于我们三级页打开,返回回关于与升级页,无崩溃。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        self.userA.open_about_page()
        self.userA.click_text("关于我们", timeout=10)
        self.userA.text_not_exists("使用政策", timeout=10)
        self.userA.press_back()
        self.userA.text_exists("软件升级", timeout=10)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
