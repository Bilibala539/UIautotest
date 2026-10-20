# CASE-ID: search-NEG-002
"""Swan 回归·搜索：注入串提交不崩溃(search-NEG-002)。

步骤→AW 映射：
- 进搜索输入页 → open_search_input_page（推荐 Tab 搜索条，现状口径）
- 3 条注入串逐条提交（值内联于方法内列表；ASCII 无 % 字符，可经驱动
  input_text 保真输入）→ click hint + input_text + 搜索按钮 [图]
- 每条提交后断言页面功能正常（空态 [图] / '没有找到相关结果' [OCR] /
  结果顶 Tab 行 '单曲' [OCR] 三者其一），随后 press_back 退回历史态
- 最后正常词恢复搜索 → submit_search_keyword('synthkw-restore')，
  断言结果顶 Tab 行渲染（mixin 内）

⚠️ 注记：注入串含标点，OCR 对特殊字符保真度不足——省略逐字回显断言
（避免 OCR 误读伪失败）；崩溃类断言（无 ANR/不闪退）由页面可继续交互
间接承载。App 全局异常捕获兜底由框架冷启动夹具承担，用例不 try/except。
cleanup：无（搜索历史留注入串，随冷启动复位语义可接受）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_HOME_MUSIC_SEARCH_BAR,
    SWAN_SEARCH_EMPTY,
    SWAN_SEARCH_SUBMIT,
)
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestInjectionStringNoCrash(SwanRP03Mixin, BaseTest):
    """注入串逐条提交，App 不崩溃且页面功能可恢复。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_injection_string_no_crash(self):
        """3 条注入串提交后断言页面功能正常，末尾正常词恢复搜索。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_MUSIC_SEARCH_BAR,
            ocr_fallback='跨平台搜索音乐')

        for payload in ("';--DROP songs", "<script>alert(1)</script>",
                        "../../etc/passwd"):
            self.userA.click_text('搜索歌曲或艺术家等', timeout=10)
            self.userA.input_text(payload)
            self.userA.click_image(SWAN_SEARCH_SUBMIT, timeout=10)
            functional = (
                self.userA.find_image(SWAN_SEARCH_EMPTY, timeout=8) is not None
                or self.userA.find_text_by_ocr('没有找到相关结果', timeout=3) is not None
                or self.userA.find_text_by_ocr('单曲', timeout=3) is not None)
            assert functional, f"注入串提交后无空态/无结果行，页面功能异常: {payload!r}"
            self.userA.press_back()

        self.userA.submit_search_keyword('synthkw-restore')

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在结果页（正常词 'synthkw-restore'）
