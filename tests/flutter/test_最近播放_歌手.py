"""Swan 回归·收藏历史域：最近播放按分类断言（回归用例 56-68）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域7）：
- 用例56-68 最近播放在历史页按分类出现 → assert_recent_played(kind, name)
  （13条合1；歌曲类配置 SWAN_HISTORY_FRESH_PLAY=1 时现场播放造数据）

各分类条目名经 SWAN_HISTORY_* 环境变量注入（未配置该类 skip）；歌曲类
复用 SWAN_TEST_SONG。rig 环境变量与公共前置/清理见
utils/aw/business/swan_regression.py。
清理（G3/G4）：收播放页 → 退出 push 页 → go_home（mixin teardown）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanContentRegressionMixin


class TestRecentPlayed(SwanContentRegressionMixin, BaseTest):
    """最近播放按分类断言（回归用例 56-68）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_recent_played(self):
        """用例56-68：最近播放按分类断言条目存在（条目名未配置则 skip）。

        歌曲类条件造数（run5 改版）：SWAN_HISTORY_FRESH_PLAY 配置时先探测
        目标曲是否已在最近播放可见（recent_played_visible），可见直接断言
        不造数；不可见才现场播放 3s 造记录（name 须为 rig 我喜欢歌单中的
        歌曲名）再断言——避免已有记录时的重复造数开销。
        """
        kind = '歌手'
        env_key = 'SWAN_HISTORY_ARTIST'
        name = os.environ.get(env_key, "").strip()
        if not name:
            pytest.skip(f"未配置 {env_key}（rig 播放记录中的条目名）")
        if kind == "歌曲" and os.environ.get("SWAN_HISTORY_FRESH_PLAY", "").strip() \
                and not self.userA.recent_played_visible(kind, name):
            # 现场播放造历史数据：点名播放 3s（确保最近播放落库，main
            # 拍板 3-5s 口径）即暂停（rig 卫生，避免音箱持续出声）
            self._preset_playing_on_favorite(source=name, mode="song")
            self.userA.sleep(3.0)
            self.userA.player_control("pause")
        self.userA.assert_recent_played(kind, name)

    def teardown(self) -> None:
        """G3/G4 清理链由 mixin teardown 承担（本用例无自定义清理）。"""
        super().teardown()