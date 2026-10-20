# CASE-ID: ai-POS-007
"""Swan 回归·AI 助手域：角色主页数据加载与系统/自定义分组渲染（ai-POS-007）。

步骤 → AW 映射：
1-2. 进入 AI 首页等待角色列表加载 → go_top_tab("AI") +
     mixin assert_ai_home_gallery（系统角色必有——基线账号画廊
     惠威百科/小薇/惠声远已实测渲染）
3. 系统角色分组 → AI 首页聚焦卡问候语（你好，我是你的好朋友，小薇）
   + mixin open_ai_roles_page 断言系统组 4 行
4. 自定义角色分组 → 管理页「自定义」节头 + 空态「暂未自定义角色」
   （基线账号无自定义角色——空态渲染即 SKIP-DATA 场景的如实断言面）
5. 横滑浏览画廊全部角色卡 → mixin swipe_ai_gallery_card next/prev 往返，
   每步画廊锚回归（全部卡可达无白屏；MP4 头像出图为视觉面不在 OCR 断言域）

cleanup：无（只读浏览；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiRoleGroupsRendering(SwanRM09Mixin, BaseTest):
    """角色主页系统/自定义分组渲染与画廊横滑。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_ai_role_groups_rendering(self):
        """系统/自定义分组渲染完整，画廊横滑往返无白屏。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.assert_ai_home_gallery()
        # 系统组聚焦卡问候语
        assert self.userA.text_exists("好朋友", timeout=8) is not None, (
            "AI 首页聚焦卡系统角色问候语「你好，我是你的好朋友，小薇」未命中 [OCR]")

        # 横滑画廊：下一张×2 + 回滑×2，每步页面锚回归
        for direction in ("next", "next", "prev", "prev"):
            self.userA.swipe_ai_gallery_card(direction)
            self.userA.assert_ai_home_gallery()

        # 管理页交叉核对分组：系统组 4 行 + 自定义组空态
        self.userA.open_ai_roles_page()
        for greeting in ("应用助手", "好朋友", "医生", "云舒雁"):
            assert self.userA.text_exists(greeting, timeout=8) is not None, (
                f"管理页系统组角色行缺失（子串「{greeting}」未命中）[OCR]")
        assert self.userA.text_exists("自定义", timeout=8) is not None, (
            "管理页「自定义」分组节头缺失 [OCR]")
        assert self.userA.text_exists("暂未自定义角色", timeout=8) is not None, (
            "管理页自定义组空态「暂未自定义角色」未渲染（基线账号无自定义角色）[OCR]")

        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
