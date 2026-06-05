"""
测试用例: 优化截图弹窗
Excel来源: 会话区及消息.xlsx 行 0-3
"""
import pytest
from conftest import BaseTest


@pytest.mark.skip(reason="系统截图触发无法在MuMu模拟器上模拟")
class TestScreenshotPopup(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    @pytest.mark.parametrize("scenario,steps,expected", [
        ("浮窗位置验证", "截图后观察浮窗位置", "浮窗位于屏幕右侧居中"),
        ("滑动消失", "向左滑动浮窗", "浮窗向右滑动并消失"),
        ("自动消失", "截图后等待4秒不操作", "浮窗自动向右滑动消失"),
        ("分享按钮触发", "点击浮窗中的分享按钮", "弹出选人组件"),
    ])
    def test_screenshot_popup(self, scenario, steps, expected):
        """优化截图弹窗验证（需真机）"""
        pass

    def teardown(self):
        pass
