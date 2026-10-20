# CASE-ID: search-POS-013
"""Swan 回归·搜索：清空历史双路径（取消保留/确认清空）(search-POS-013)。

步骤→AW 映射：
- 补历史前置 → search('ocean', entry='home') + press_back（回历史态）
- 进删除模式 → enter_search_history_delete_mode()
- 路径一：点'清空' → 确认弹窗点'取消' → text_exists('ocean')（历史保留）
- 路径二：再点'清空' → 弹窗点'清空'确认 → text_not_exists('ocean')
  （历史清空）+ '完成' 文案消失（自动退出删除模式的可观察证据）

⚠️ 注记：清空确认弹窗按钮文案以 YAML 锚点（清空/取消）承载；历史 ≥1 条
由用例自建（同 POS-012 口径）。
cleanup：无（历史清空即用例自身结果态）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestClearHistoryDoublePath(SwanRP03Mixin, BaseTest):
    """清空历史：取消路径保留、确认路径清空并自动退出删除模式。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_clear_history_double_path(self):
        """取消保留历史 → 确认清空 → 历史为空并退出删除模式。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.search('ocean', entry='home')
        self.userA.press_back()
        self.userA.text_exists('ocean', timeout=5)

        self.userA.enter_search_history_delete_mode()

        # 路径一：取消 → 保留
        self.userA.click_text('清空', timeout=5)
        self.userA.click_text('取消', timeout=5)
        self.userA.text_exists('ocean', timeout=5)

        # 路径二：确认清空
        self.userA.click_text('清空', timeout=5)
        self.userA.click_text('清空', timeout=5)
        self.userA.text_not_exists('ocean', timeout=5)
        assert self.userA.find_text_by_ocr('完成', timeout=3) is None, (
            "确认清空后仍可见'完成'——未自动退出删除模式")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在搜索历史空态
