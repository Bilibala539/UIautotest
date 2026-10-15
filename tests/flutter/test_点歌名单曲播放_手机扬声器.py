"""Swan 回归·播放器域：我喜欢页点歌名单曲播放（回归用例 14）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域3）：
- 用例14 我喜欢页点歌名单曲播放 → start_play(mode="song")
  （歌名经 SWAN_TEST_SONG 注入，未配置自动 skip）

矩阵：device_type（speaker=手机扬声器默认输出 / wifi_device=rig 音箱
SWAN_DEVICE_NAME）。
rig 环境变量与公共前置/清理见 utils/aw/business/swan_regression.py。
清理（G3/G4）：关弹层 → 尽力暂停 → 收播放页 → 输出恢复 → 回首页（mixin teardown）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin



class TestPlaySingleSong(SwanPlayerRegressionMixin, BaseTest):
    """我喜欢页点歌名单曲播放（回归用例 14）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_play_single_song(self):
        """用例14：我喜欢页点歌名单曲播放（SWAN_TEST_SONG 未配置则 skip）。"""
        if not self.SONG_NAME:
            pytest.skip("未配置 SWAN_TEST_SONG（rig 我喜欢歌单中的歌曲名）")
        self.userA.preset_playing('speaker', source=self.SONG_NAME, mode="song")
        self.userA.assert_now_playing(self.SONG_NAME)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
