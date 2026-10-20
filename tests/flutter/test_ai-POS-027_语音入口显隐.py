# CASE-ID: ai-POS-027
"""Swan 回归·AI 助手域：语音输入模式按钮显隐与模式切换（ai-POS-027）。

步骤 → AW 映射：
1. 普通角色对话页断言语音输入入口 → open_ai_chat_by_role("小薇") +
   probe_image(SWAN_AI_CHAT_VOICE_BTN)（已注册 [图] 锚）
2. 切换至语音输入模式 → click_image(SWAN_AI_CHAT_VOICE_BTN) 后轮询
   「按住说话」文本（语音模式 UI 的可观察面；若首点弹系统麦克风权限弹窗，
   执行轮以返回键关闭后重跑——权限授予态需人工预置）
3. 切回文本模式 → press_back 关闭语音模式（绝不触碰「按住说话」控件——
   硬约束 AiVoiceCapturePort 零启动），断言语音 UI 关闭、页面回到
   对话页或 AI 首页（两种收口形态执行轮如实记录）

分支说明：roleId==12 官方知识库角色「语音入口不存在」分支因卡位与
roleId 映射未探索（无 OCR 锚识别哪张卡为 roleId==12）未覆盖，
见 package_report.json notes。

cleanup：无（全程零采集触发、零 wav 文件；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_AI_CHAT_VOICE_BTN
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiVoiceModeToggle(SwanRM09Mixin, BaseTest):
    """语音输入模式按钮显隐与模式切换（不启动采集）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_voice_mode_toggle(self):
        """语音入口可见，切换出「按住说话」UI，返回后语音 UI 关闭。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_chat_by_role("小薇")

        # 语音输入入口可见
        assert self.userA.probe_image(SWAN_AI_CHAT_VOICE_BTN, timeout=5) is not None, (
            "普通角色对话页语音输入入口 [图] 未命中（SWAN_AI_CHAT_VOICE_BTN）")

        # 切换至语音输入模式（零采集：不按住说话）
        self.userA.click_image(SWAN_AI_CHAT_VOICE_BTN, timeout=10)
        assert self.userA.find_text_by_ocr("按住说话", timeout=10) is not None, (
            "点击语音按钮后未出现「按住说话」语音模式 UI（可能被麦克风权限"
            "系统弹窗拦截，或模式切换 UI 形态需标定）[OCR]")

        # 切回文本模式：返回键关闭语音模式（零采集触发）
        self.userA.press_back()
        assert self.userA.find_text_by_ocr("按住说话", timeout=3) is None, (
            "返回后语音模式 UI 仍在前台（未切回）[OCR]")
        assert self.userA.assert_any_text(("发送消息", "添加更多AI角色"), timeout=8), (
            "语音模式关闭后未回到对话页或 AI 首页（页面态异常）[OCR]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
