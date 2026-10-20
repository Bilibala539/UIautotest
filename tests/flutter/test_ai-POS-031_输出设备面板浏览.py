# CASE-ID: ai-POS-031
"""Swan 回归·AI 助手域：输出设备选择面板打开与同源展示（ai-POS-031）。

步骤 → AW 映射：
1. 对话页点击输出设备入口 → go_top_tab("AI") + open_ai_chat_by_role("小薇")
   + click_text("暂无设备")（设备副标题 chip 为入口——可点性未探索，
   锚待标定，见 report.template_needs）
2. 弹层设备列表加载 → probe_image(SWAN_DEVICE_SHEET_TITLE)（AI 朗读设备
   弹层与切换设备弹层共用设备列表/标题行）+ 断言「手机扬声器」设备项渲染
   （与设备页同源数据的最小可观察面；rig 真实音箱行名依账号设备而定，
   不作硬断言）
3-4. 不选中直接关闭 → press_back（⛔ 全程不点选任何设备行——选中写
   closeAudio='2' 协议参数并持久化，禁区 6）→ 断言对话页恢复、副标题
   「暂无设备」原样（输出目标零变化）

cleanup：无（零写零选中；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_DEVICE_SHEET_TITLE
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiOutputDevicePanelOpen(SwanRM09Mixin, BaseTest):
    """输出设备选择面板打开与数据源同源展示（零选中）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_output_device_panel_open_close(self):
        """面板打开、设备项渲染、关闭零写副标题原样。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_chat_by_role("小薇")

        # 打开输出设备弹层（副标题 chip 入口，锚待标定）
        self.userA.click_text("暂无设备", timeout=10)
        assert self.userA.probe_image(SWAN_DEVICE_SHEET_TITLE, timeout=8) is not None, (
            "点击设备副标题后弹层标题行 [图] 未命中（入口锚或弹层形态需标定）")
        assert self.userA.text_exists("手机扬声器", timeout=8) is not None, (
            "输出设备弹层未见「手机扬声器」设备项（同源列表未加载）[OCR]")

        # 不选中直接关闭（⛔ 不点任何设备行）
        self.userA.press_back()
        assert self.userA.text_exists("发送消息", timeout=8) is not None, (
            "弹层关闭后未回到对话页 [OCR]")
        assert self.userA.find_ai_topbar_text("暂无设备", timeout=5) is not None, (
            "关闭弹层后设备副标题变化（发生非预期输出目标写）[OCR·顶栏区]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
