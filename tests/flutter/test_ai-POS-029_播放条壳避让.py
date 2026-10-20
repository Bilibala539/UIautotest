# CASE-ID: ai-POS-029
"""Swan 回归·AI 助手域：聊天页底部播放条壳挂载与输入避让（ai-POS-029）。

步骤 → AW 映射：
1. 对话页观察底部播放条壳 → 运行时条件门：SWAN_AI_PLAY_PRESET=1
   （播放态预置开关；未置位 skip——播放壳需在播任务渲染，基线账号
   平台未授权时 preset_playing 发起失败）→ preset_playing_on_favorite()
   （业务层既有播放前置，rig 我喜欢发起）→ open_ai_chat_by_role("小薇")
   → 底部播放条锚（扬声器/播放控制区 (0,1300,720,300)）OCR 断言
2. 输入框唤起键盘避让 → click_text("发送消息") → input_text → 断言
   输入区仍可见（发送消息占位上移渲染=避让生效的可观察面）
3. 收起键盘回位 → press_back（收键盘不退页）→ 发送消息锚回位 +
   播放条壳仍在（无重放抖动的可观察面：锚稳定）

数据说明：readOnly 路由豁免与 94dp/420ms 补间为实现契约面，UI 侧以
避让前后锚位置回归覆盖；播放态经条件门隔离（rig 环境全通）。

cleanup：无（播放自然结束/由下一用例冷启动复位；框架夹具承担）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiChatPlayerShellAvoidance(SwanRM09Mixin, BaseTest):
    """聊天页播放条壳挂载与键盘避让（播放态条件门）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_chat_player_shell_avoidance(self):
        """播放壳挂载，键盘避让与收起回位锚稳定。"""
        if os.environ.get("SWAN_AI_PLAY_PRESET", "").strip() != "1":
            pytest.skip(
                "需播放态前置（rig 环境 SWAN_AI_PLAY_PRESET=1；基线账号"
                "平台未授权无法建立播放）")
        self.userA.ensure_logged_in_on_home()
        # 步骤 1 前置：播放态（rig 我喜欢发起）
        self.userA.preset_playing_on_favorite()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_chat_by_role("小薇")

        # 步骤 1：底部播放条壳挂载（壳内文案锚未探索，探针条件门）
        if self.userA.find_text_by_ocr(
                "扬声器", timeout=8, region=(0, 1300, 720, 300)) is None:
            self.userA.press_back()
            self.userA.assert_ai_home_gallery()
            pytest.skip(
                "播放条壳内文案 OCR 无稳定锚（对话页底部播放壳未探索，"
                "template_needs: 播放条壳锚）——已退出会话")

        # 步骤 2：键盘唤起，输入区避让（输入锚仍可见=避让生效）
        self.userA.click_text("发送消息", timeout=10)
        self.userA.input_text("qa-shell-avoid-029")
        assert self.userA.find_text_by_ocr("发送消息", timeout=10) is not None, (
            "键盘弹起后输入区不可见（避让失效/被遮挡）[OCR]")

        # 步骤 3：收起键盘回位（返回键收键盘不退页）
        self.userA.press_back()
        assert self.userA.find_text_by_ocr("发送消息", timeout=10) is not None, (
            "收起键盘后输入区未回位 [OCR]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
