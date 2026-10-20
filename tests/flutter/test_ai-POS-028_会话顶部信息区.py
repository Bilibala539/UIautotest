# CASE-ID: ai-POS-028
"""Swan 回归·AI 助手域：对话页顶部角色信息与设备副标题展示（ai-POS-028）。

步骤 → AW 映射：
1. 普通角色对话页顶部信息区 → go_top_tab("AI") + mixin
   open_ai_chat_by_role("小薇")（聊天页双锚内含）+ 顶栏区断言角色名「小薇」
2. 朗读设备副标题（空态面）→ 基线账号对话页未绑定朗读设备，副标题渲染
   空态文案「暂无设备」（overallExpect：无绑定设备则断言空态合理；
   wave5 实测副标题行 y≈165-195 在顶栏区域内）
3. roleId==12 官方知识库角色对比分支：卡位与 roleId 映射未探索（无 OCR 锚
   识别哪张卡为 roleId==12），该分支未覆盖——见 package_report.json notes。

cleanup：无（只读断言；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiChatTopInfoArea(SwanRM09Mixin, BaseTest):
    """对话页顶部角色信息与设备副标题展示。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_chat_top_info_and_device_subtitle(self):
        """顶栏角色名 + 设备副标题空态「暂无设备」渲染。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_chat_by_role("小薇")

        # 顶栏角色名 + 设备副标题（空态：未绑定朗读设备）
        assert self.userA.find_ai_topbar_text("小薇", timeout=5) is not None, (
            "对话页顶栏区未渲染角色名「小薇」[OCR·顶栏区]")
        assert self.userA.find_ai_topbar_text("暂无设备", timeout=5) is not None, (
            "对话页设备副标题未渲染空态「暂无设备」（绑定态展示需人工预置设备）[OCR·顶栏区]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
