# CASE-ID: profile-NEG-003
"""Swan 回归·M13 个人中心：顶卡快照往返不重拉（profile-NEG-003）。

用例 → AW 映射：
- 读取顶卡昵称与明文手机号 → me_top_nickname（OCR 顶卡块）+ text_exists(userA.phone)
- 切首页再切回我的 → go_bottom_tab 往返
- 断言昵称字符串一致、手机号仍显（快照缓存，无重拉闪变）
- 顶卡进出个人资料页后再次比对
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg003SnapshotNoRepull(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_me_top_snapshot_stable(self) -> None:
        self.userA.open_me_page()
        nickname_first = self.userA.me_top_nickname()
        self.userA.text_exists(self.userA.phone, timeout=5)
        # 切首页再切回我的
        self.userA.go_bottom_tab("首页")
        self.userA.go_bottom_tab("我的")
        nickname_second = self.userA.me_top_nickname()
        assert nickname_second == nickname_first, \
            f"Tab 往返后顶卡昵称变化: {nickname_first!r} → {nickname_second!r}"
        self.userA.text_exists(self.userA.phone, timeout=5)
        # 顶卡进出个人资料页后顶卡数据保持
        self.userA.open_person_info()
        self.userA.back_to_me_page()
        assert self.userA.me_top_nickname() == nickname_first, "进出资料页后顶卡昵称变化"
        self.userA.text_exists(self.userA.phone, timeout=5)

    def teardown(self) -> None:
        pass
