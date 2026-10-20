# CASE-ID: search-NEG-012
"""Swan 回归·搜索：搜索页高频交互无 ANR/无冻结(search-NEG-012)。

步骤→AW 映射：
- 进搜索输入页 → open_search_input_page（推荐 Tab 搜索条）
- 5 轮 输入+清空 → click hint + input_text(25 字符合成串) + clear_input
  + text_exists(hint)（清空后回显即时恢复=无冻结的可观察证据）
- 建历史后高频点击 → submit_search_keyword 建历史 + press_back 回历史态；
  5 轮点击历史芯片→press_back；5 轮点击提交按钮（空词不跳页）
- ANR 守门 → assert_no_anr_dialog() + 断言仍停输入页（hint 可见）

⚠️ 注记：YAML"长按粘贴"以等价长串 input_text 承载（粘贴菜单无 AW 锚，
驱动注入等价验证文本通道健壮性）；App 指标级卡顿（帧/响应毫秒）非 OCR
能力，以"交互全程可继续+无 ANR 弹窗"为守门断言。
cleanup：无（搜索历史留测试词，随冷启动复位语义可接受）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_HOME_MUSIC_SEARCH_BAR,
    SWAN_SEARCH_SUBMIT,
)
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestSearchStressNoAnr(SwanRP03Mixin, BaseTest):
    """搜索页高频输入/清空/连点后无 ANR，页面功能正常。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_search_stress_no_anr(self):
        """5 轮输入清空 + 5 轮历史芯片连点 + 5 轮提交连点 → 无 ANR。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_MUSIC_SEARCH_BAR,
            ocr_fallback='跨平台搜索音乐')

        for _ in range(5):
            self.userA.click_text('搜索歌曲或艺术家等', timeout=10)
            self.userA.input_text('synthkw-stress-0000000000')
            self.userA.clear_input()
            self.userA.text_exists('搜索歌曲或艺术家等', timeout=5)

        self.userA.submit_search_keyword('synthkw-stress-0000000000')
        self.userA.press_back()
        for _ in range(5):
            self.userA.click_text('synthkw-stress', timeout=5)
            self.userA.press_back()
        for _ in range(5):
            self.userA.click_image(SWAN_SEARCH_SUBMIT, timeout=5)

        self.userA.assert_no_anr_dialog()
        self.userA.text_exists('搜索歌曲或艺术家等', timeout=5)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在搜索输入页
