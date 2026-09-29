"""Swan 回归·导航/收藏历史/搜索域公共前置与清理（域 4/7/8 三个用例文件共用）。

非用例模块（无 test_ 前缀，pytest 与 run_parallel 均不收集）。

为什么新建本文件而不并入 swan_regression_common.py：
- 本批用例收尾态常在 push 页（歌单详情/播放历史/搜索结果），这些页无
  底部 4 tab，teardown 需要「收播放页 -> 逐级 press_back 退出 push 页 ->
  回全局 tab 壳 -> go_home」的反向退出序列，与播放器域 teardown（tab 壳 +
  播放页两态）结构不同；
- 播放器域公共文件保持只读（前批已交付），避免跨域改动互相影响。

继承 SwanPlayerRegressionMixin：复用登录（_ensure_logged_in_on_home）、
顶 Tab 复位（_stay_on_recommend_tab）、播放前置辅助（_close_sheet_if_any /
_pause_if_playing / _dismiss_player_if_any）与 rig 环境变量，仅覆盖 teardown。

新代码定位一律图像模板 > OCR 文本（方案 §0）；唯一例外仍是 teardown 收尾
的 go_home() 存量 key 导航（迁移待拍板，见 docs/待办与缺口清单.md「定位策略
定稿」节）。

rig 环境变量（本批新增，均可在不配置时走默认/skip）：
- SWAN_FAV_PLATFORMS       用例41-43 平台代码列表，逗号分隔（默认 swan；
                           第三方平台须授权态，见方案 §5⑤）
- SWAN_COLLECT_PLATFORMS   用例44-55 目标歌单平台代码列表（默认 swan）
- SWAN_COLLECT_PLAYLIST    用例44-55 目标歌单名（默认 我的音乐；收藏结果
                           无自动化回滚，见 SwanBusiness.collect_song 注记）
- SWAN_COLLECT_PLAYER_SONG 用例44-55 source="player" 分支的收藏曲（默认
                           回落 SWAN_TEST_SONG；run5 改版——原「播放全部
                           首曲」疑已在目标歌单触发重复收藏拦截，改为点
                           名播放指定曲；数据一次性约定见 test_collect_song 注）
- SWAN_COLLECT_SOURCE_PLAYLIST
                           用例44-55 source="playlist_page" 的收藏源歌单
                           （默认 我的家庭）。⚠️ 数据态耗尽运维口径（方案
                           A，run5 拍板）：预校验 skip 报「数据态耗尽」时
                           轮换本变量指向顶行曲不在目标歌单内的歌单，或由
                           设备管理流程清理目标歌单；用例预校验（方案 C）
                           保证耗尽时诚实 skip 不产假红
- SWAN_HISTORY_PLAYLIST / SWAN_HISTORY_ARTIST / SWAN_HISTORY_ALBUM /
  SWAN_HISTORY_RADIO / SWAN_HISTORY_PODCAST
                           用例56-68 各分类断言条目名（未配置该类 skip）；
                           歌曲类复用播放器域 SWAN_TEST_SONG，配置
                           SWAN_HISTORY_FRESH_PLAY=1 时现场播放造历史数据
- SWAN_SEARCH_KEYWORD_<tab> 用例69-72 各分类搜索关键词（默认 piano，
                           英文；adb 中文输入不可达）
- SWAN_SEARCH_PLATFORMS    已授权平台代码列表，逗号分隔（如 "qq,netease"；
                           配置后 assert_search_results 对所列平台断言
                           「有结果」，账号 B 已授权口径；默认空 -> 断言
                           空态，干净未授权账号稳定态。两种口径见
                           SwanBusiness.assert_search_results docstring）
"""
from __future__ import annotations

import os

from tests.flutter.swan_regression_common import SwanPlayerRegressionMixin


class SwanContentRegressionMixin(SwanPlayerRegressionMixin):
    """导航/收藏历史/搜索域回归用例 mixin：push 页反向退出式清理。"""

    FAVORITE_PLATFORMS = [p.strip() for p in
                          os.environ.get("SWAN_FAV_PLATFORMS", "swan").split(",")
                          if p.strip()]
    COLLECT_PLATFORMS = [p.strip() for p in
                         os.environ.get("SWAN_COLLECT_PLATFORMS", "swan").split(",")
                         if p.strip()]
    COLLECT_PLAYLIST = os.environ.get("SWAN_COLLECT_PLAYLIST", "我的音乐")
    # source="player" 分支收藏曲：显式配置优先，回落 SWAN_TEST_SONG（rig
    # 我喜欢页已验证可达的歌名，见 start_play mode="song" 注）——二者皆空
    # 时 collect_song[player] 走播放全部首曲（数据一次性约定，见
    # test_collect_song 注）
    COLLECT_PLAYER_SONG = (os.environ.get("SWAN_COLLECT_PLAYER_SONG", "").strip()
                           or os.environ.get("SWAN_TEST_SONG", "").strip())

    def teardown(self):
        """G3/G4：关弹层（设备弹层+音量弹层）-> 尽力暂停 -> 收播放页 ->
        退出 push 页 -> 回首页。

        本批用例常停在 push 页（无底部 4 tab，直接 go_home 的 key 点击会
        失败），须先 back_to_tab_shell [图] 逐级退出，再走存量 go_home
        （key 导航迁移待拍板例外）。
        音量弹层探测关闭继承播放器域 teardown 的 run4b 结论
        （_close_volume_popup_if_any）。
        """
        self._close_sheet_if_any()
        self._close_volume_popup_if_any()
        self._pause_if_playing()
        self._dismiss_player_if_any()
        self.user.back_to_tab_shell()
        self.user.go_home()

    def _preset_playing_on_favorite(self, source: str = "favorite",
                                    mode: str = "all") -> None:
        """播放前置（本批用例）：推荐顶 Tab -> 我喜欢卡 [OCR] -> 发起播放。

        与播放器域 _preset_playing("speaker") 的差别仅在到位断言：按任务
        约束改用 OCR 页面判据「宝藏音乐，随心收藏」（我喜欢页特有，知识库
        生效断言），不复用含"0首歌"计数的 SWAN_FAVORITE_PLAY_ALL 模板
        （歌单加歌后失配，见 image/image_name_mapping.py 注记）。
        播放发起仍复用域3 start_play（不重写播放逻辑）。
        """
        self._ensure_logged_in_on_home()
        self._stay_on_recommend_tab()
        self.aw.click_text("我喜欢", timeout=10)                  # 我喜欢卡片 [OCR]
        self.aw.text_exists("宝藏音乐，随心收藏", timeout=15)     # 我喜欢页判据 [OCR]
        self.user.start_play(source=source, mode=mode)
