# CASE-ID: search-POS-023
"""Swan 回归·搜索：全链B 全国电台详情入口→搜索→电台播放(search-POS-023,B 级,部分转换)。

步骤→AW 映射（电台详情页知识库未探索，按 ADD1 口径照常产出）：
- 前置：授权探针（网易云行未授权态 [图]）→ 未授权 skip；合成词经环境
  变量 SWAN_SEARCH_KEYWORD_RADIO 注入（缺省 'synthkw-radio'，执行轮
  替换为测试服可命中电台的合成词——YAML data 标注执行轮替换）
- 链路：电台 Tab 全国区块 → 电台卡 → 详情 → 详情搜索入口 → 搜索页
  （同 search-POS-008 链；入口探测缺失即 template_needs 断言）
- 提交合成词 → submit_search_keyword(keyword)（结果页就绪探针）
- 切电台 Tab → click_text('电台', region=结果顶 Tab 行)
- 播放任一电台条目 → play_first_song_result()（OCR 首行动态点击 +
  底部播放条 [图] 出现断言，经统一播放入口开始播放）

⚠️ 部分转换注记：分组过滤一致性（stationTerraceType 仅 '0'，无 '5'/'6'
混入）——归属码值 OCR 不可读（结果行无归属标识文案，TCBATCH1-ADD1
口径下非"页面未探索"而属数据语义层不可观测），以链路可达+电台 Tab
渲染+播放条出现承载；过滤语义缺口记录于报告 notes。
cleanup：播放为会话态无持久写（YAML cleanup 口径），teardown pass。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestFullChainBRadioSearchPlay(SwanRP03Mixin, BaseTest):
    """全链B：全国电台详情→搜索→电台 Tab→播放电台条目。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_full_chain_b_radio_search_play(self):
        """电台卡→详情→搜索入口→合成词→电台 Tab→播放首条→播放条。"""
        keyword = os.environ.get("SWAN_SEARCH_KEYWORD_RADIO", "").strip() or "synthkw-radio"

        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab('平台')
        if self.userA.find_image(SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
                                 timeout=3) is not None:
            pytest.skip("账号未授权平台（网易云行未授权态 [图] 命中）——"
                        "电台内容有授权门禁；授权后自动恢复")
        self.userA.go_bottom_tab('首页')

        self.userA.go_top_tab('电台')
        self.userA.text_exists('全国电台', timeout=15)
        self.userA.tap_first_row_below_anchor('全国电台')
        assert self.userA.find_text_by_ocr('搜索', timeout=5) is not None, (
            "电台详情页未探测到搜索入口——template_needs 已登记锚图")
        self.userA.click_text('搜索', timeout=5)
        self.userA.text_exists('搜索歌曲或艺术家等', timeout=10)

        self.userA.submit_search_keyword(keyword)
        self.userA.click_text('电台', timeout=5, region=(0, 190, 720, 130))
        self.userA.play_first_song_result()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在搜索结果页电台 Tab（播放态随冷启动复位）
