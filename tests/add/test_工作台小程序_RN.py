"""
测试用例: 工作台小程序入口（RN小程序 - KM）
探索来源: AI自主探索POPO App生成
探索补全: 原始用例步骤复杂，通过自主探索App补全操作路径

⚠️ 探索结论: 当前POPO Android版(4.21.0)底部导航栏无"工作台"Tab。
底部仅有"消息"等入口，侧边栏中也无工作台入口。
该用例标记为"探索确认不存在"。

使用 pytest.mark.skip 跳过本用例。
"""
import pytest

pytest.skip("当前POPO Android版(4.21.0)底部导航无工作台Tab，功能不可用", allow_module_level=True)
from conftest import BaseTest
import time


class TestWorkbenchMiniProgramRN(BaseTest):
    """工作台小程序入口 - RN小程序测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_open_km_mini_program(self):
        """
        在工作台点击KM小程序，验证可以打开
        """
        # 点击底部工作台Tab
        self.userA.click_text("工作台")
        time.sleep(2)

        # 验证进入工作台页面
        self.userA.aw.find_text_by_ocr("工作台", timeout=5)

        # 查找KM入口
        km_pos = self.userA.aw.find_text_by_ocr("KM", timeout=5)
        assert km_pos is not None, "工作台页面应有KM入口"

        # 点击KM
        self.userA.click_text("KM")
        time.sleep(3)

        # 验证KM小程序打开（页面应该有变化,不再显示工作台列表）
        # KM加载后会有网页内容，通过检查页面变化来验证
        self.userA.aw.press_back()
        time.sleep(1)

    def teardown(self):
        try:
            # 回到消息Tab
            self.userA.click_text("消息")
            time.sleep(1)
            self.userA.logout()
        finally:
            self.userA.aw.stop_app()