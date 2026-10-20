# CASE-ID: ai-POS-034
"""Swan 回归·AI 助手域：输出设备面板仅浏览零写还原（ai-POS-034）。

步骤 → AW 映射：
1. 打开输出设备弹层 → go_top_tab("AI") + open_ai_chat_by_role("小薇") +
   click_text("暂无设备")（入口锚待标定，见 report.template_needs）
2. 逐项浏览设备项 → probe_image(SWAN_DEVICE_SHEET_TITLE) +
   「手机扬声器」设备项断言（⛔ 全程不点选——chatingAiSelectedUiDeviceList
   持久化零触碰）
3. 不选中直接关闭 → press_back → 对话页恢复
4. 重新打开弹层核对再关闭 → 二次打开断言设备项仍在（弹层状态无残留），
   关闭后副标题「暂无设备」原样（输出目标/持久化零写还原的可观察面）

cleanup：无（零写零选中；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_DEVICE_SHEET_TITLE
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiOutputDevicePanelReadOnly(SwanRM09Mixin, BaseTest):
    """输出设备面板仅浏览零写还原。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_output_device_panel_readonly(self):
        """两次打开-关闭弹层，设备项渲染稳定，副标题零写还原。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_chat_by_role("小薇")

        # 第一次打开-关闭
        self.userA.click_text("暂无设备", timeout=10)
        assert self.userA.probe_image(SWAN_DEVICE_SHEET_TITLE, timeout=8) is not None, (
            "输出设备弹层标题行 [图] 未命中（入口锚或弹层形态需标定）")
        assert self.userA.text_exists("手机扬声器", timeout=8) is not None, (
            "输出设备弹层未见「手机扬声器」设备项 [OCR]")
        self.userA.press_back()
        assert self.userA.text_exists("发送消息", timeout=8) is not None, (
            "弹层关闭后未回到对话页 [OCR]")

        # 重新打开核对（持久化零写：弹层可再次正常打开）再关闭
        self.userA.click_text("暂无设备", timeout=10)
        assert self.userA.probe_image(SWAN_DEVICE_SHEET_TITLE, timeout=8) is not None, (
            "二次打开输出设备弹层失败（首次浏览产生异常状态）")
        assert self.userA.text_exists("手机扬声器", timeout=8) is not None, (
            "二次打开后设备项缺失 [OCR]")
        self.userA.press_back()
        assert self.userA.find_ai_topbar_text("暂无设备", timeout=5) is not None, (
            "两次仅浏览后设备副标题变化（发生非预期持久化写）[OCR·顶栏区]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
