# CASE-ID: ai-POS-016
"""Swan 回归·AI 助手域：音色列表加载与选择回显（止步保存前）（ai-POS-016）。

步骤 → AW 映射：
1. 进入角色编辑器（新建分型）→ go_top_tab("AI") + mixin open_ai_role_editor()
2. 打开音色选择区 → swipe_up 滚至 *语音选择 节（wave5 实测 2-3 屏后列表可见：
   知楠/知琪/知厨/知德/知佳/知茹）
3. 浏览音色列表 → 断言表单回显行（_AI_VOICE_FORM_REGION 区域限定当前音色
   「知楠」）与列表行「知琪」并存（区域区分同文案）
4. 选择一个音色 → click_text("知琪") 后断言表单回显区变为「知琪」（选中态
   回显到编辑器表单的可观察面——若点选不即时回显需执行轮标定，
   见 report.template_needs）
5. 不保存直接返回 → press_back 零写退出（不触碰 完成——⛔ 服务端角色写）

cleanup：无（止步保存前零写；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiVoiceListSelectEcho(SwanRM09Mixin, BaseTest):
    """音色列表加载与选择回显（止步保存前零写）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_voice_list_select_echo(self):
        """音色列表非空，点选知琪后表单回显区由知楠变为知琪。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_role_editor()

        # 滚至语音选择节，列表渲染
        self.userA.swipe_up()
        self.userA.swipe_up()
        assert self.userA.text_exists("语音选择", timeout=8) is not None, (
            "编辑器 *语音选择 节未滚入视野 [OCR]")
        # 表单回显行（当前音色）与列表行区域区分：回显区默认知楠，列表含知琪
        assert self.userA.find_ai_voice_form_text("知楠", timeout=8) is not None, (
            "音色表单回显区未见默认音色「知楠」[OCR·表单区]")
        assert self.userA.text_exists("知琪", timeout=8) is not None, (
            "音色列表行「知琪」未渲染（列表非空断言失败）[OCR]")

        # 点选知琪 → 表单回显区变为知琪（单选回显可观察面）
        self.userA.click_text("知琪", timeout=10)
        assert self.userA.find_ai_voice_form_text("知琪", timeout=10) is not None, (
            "点选知琪后表单回显区未变为「知琪」（点选不即时回显，需执行轮标定）[OCR·表单区]")

        # 不保存直接返回（零写退出）
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
