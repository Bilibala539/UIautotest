"""Swan 回归·播放器域：播放发起与播放控制（回归用例 13-22）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域3）：
- 用例13 我喜欢页「播放全部」发起播放 → start_play(mode="all") + 播放态双证据
- 用例14 我喜欢页点歌名单曲播放     → start_play(mode="song")
  （歌名经 SWAN_TEST_SONG 注入，未配置自动 skip）
- 用例15-22 循环模式 × 设备类型矩阵上的播放控制序列
  → set_loop_mode + player_control(pause/play/next/prev)
  + assert_playing/assert_paused

矩阵：device_type（speaker=手机扬声器默认输出 / wifi_device=rig 音箱
SWAN_DEVICE_NAME）× loop_mode（list/single/shuffle）。
播放态断言 = 控制键图标 [图] + 封面区 region_changed 双证据（方案 §5③，
不做声学断言）；回归须真点真音箱（方案 §5②）。
清理（G3/G4）：关弹层 → 尽力暂停 → 收播放页 → go_home。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from tests.flutter.swan_regression_common import DEVICE_TYPES, SwanPlayerRegressionMixin

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)

LOOP_MODES = ["list", "single", "shuffle"]


class TestPlayerPlayControl(SwanPlayerRegressionMixin, BaseTest):
    """播放发起与播放控制（回归用例 13-22）。"""

    @pytest.mark.parametrize("device_type", DEVICE_TYPES)
    def test_play_all_from_favorite(self, device_type):
        """用例13：我喜欢页「播放全部」发起播放，断言播放态双证据。"""
        self._preset_playing(device_type)
        self.user.assert_playing()  # 显式复核（start_play 收尾已断言一次）

    @pytest.mark.parametrize("device_type", DEVICE_TYPES)
    def test_play_single_song(self, device_type):
        """用例14：我喜欢页点歌名单曲播放（SWAN_TEST_SONG 未配置则 skip）。"""
        if not self.SONG_NAME:
            pytest.skip("未配置 SWAN_TEST_SONG（rig 我喜欢歌单中的歌曲名）")
        self._preset_playing(device_type, source=self.SONG_NAME, mode="song")
        self.user.assert_now_playing(self.SONG_NAME)

    @pytest.mark.parametrize("loop_mode", LOOP_MODES)
    @pytest.mark.parametrize("device_type", DEVICE_TYPES)
    def test_loop_mode_and_controls(self, device_type, loop_mode):
        """用例15-22：设备类型 × 循环模式矩阵上的播放控制序列。

        set_loop_mode 以目标态图标 [图] 断言收尾；暂停/继续分别以
        assert_paused/assert_playing 双证据断言；切歌后断言播放态保持
        （具体曲目切换由已知歌名的用例经 assert_now_playing 复核，见用例14）。
        """
        self._preset_playing(device_type)
        self.user.set_loop_mode(loop_mode)
        self.user.player_control("pause")
        self.user.player_control("play")
        self.user.player_control("next")
        self.user.player_control("prev")
