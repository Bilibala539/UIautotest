# CASE-ID: search-NEG-016
"""Swan 回归·搜索：平台内容页搜索入口无关键词残留(search-NEG-016,部分转换)。

步骤→AW 映射：
- 先在首页搜一次建"上一次搜索" → search('synthkw-residue', entry='home')
  + back_to_tab_shell()（全平台搜索后返回首页）
- 授权态探针（平台页网易云行未授权态 [图]，同既有平台内容页用例口径；
  未授权 → pytest.skip，授权后自动恢复）
- 进 QQ 音乐平台主页 → open_platform('qq')
- 平台主页搜索入口 → open_search_input_page(ocr_fallback='搜索QQ音乐')
- 断言输入框无残留 → text_not_exists('synthkw-residue')
- 空提交守门 → click_image(SWAN_SEARCH_SUBMIT) + text_not_exists('单曲')
  （结果顶 Tab 行未出现=未发搜索请求）+ text_exists(hint)（仍停输入页）
- 新词搜索可正常发起 → submit_search_keyword('synthkw-qq')

⚠️ 部分转换注记：YAML"结果仅含该平台内容"——结果内容来源归属 OCR 无法
判定（结果页无平台归属标识文案），以"平台页搜索链路可用+无残留+空提交
不发请求"为可观察断言。
cleanup：平台主页为 push 页，teardown body 一律 pass（冷启动复位）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
    SWAN_SEARCH_SUBMIT,
)
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestPlatformSearchNoResidue(SwanRP03Mixin, BaseTest):
    """QQ 音乐平台主页搜索入口：无上次关键词残留，空提交不发请求。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_platform_search_entry_no_residue(self):
        """全平台搜索后进平台页搜索入口，断言无残留+空提交守门+新词可用。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.search('synthkw-residue', entry='home')
        self.userA.back_to_tab_shell()

        # 授权态探针（代理口径同既有平台内容页用例）
        self.userA.go_bottom_tab('平台')
        if self.userA.find_image(SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
                                 timeout=3) is not None:
            pytest.skip("账号未授权平台（网易云行未授权态 [图] 命中）——"
                        "本用例需已授权态；授权后自动恢复运行")

        self.userA.open_platform('qq')
        self.userA.open_search_input_page(ocr_fallback='搜索QQ音乐')

        self.userA.text_not_exists('synthkw-residue', timeout=3)
        self.userA.click_image(SWAN_SEARCH_SUBMIT, timeout=5)
        self.userA.text_not_exists('单曲', timeout=3)
        self.userA.text_exists('搜索歌曲或艺术家等', timeout=5)

        self.userA.submit_search_keyword('synthkw-qq')

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在 QQ 音乐平台搜索结果页（push 链随冷启动复位）
