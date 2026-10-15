# CASE-ID: aw-最近播放_播客
# LINKED-CASE: home-POS-004,library-POS-037
"""Swan 回归·收藏历史域：最近播放按分类断言（回归用例 56-68）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域7）：
- 用例56-68 最近播放在历史页按分类出现 → assert_recent_played('播客', name)
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
        name = os.environ.get('SWAN_TEST_SONG', "").strip()
        if not name:
            pytest.skip(f"未配置 SWAN_TEST_SONG（rig 播放记录中的条目名）")
        self.userA.assert_recent_played('播客', name)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
