# CASE-ID: music-POS-024
"""Swan 回归·M07 网易云:私享漫游卡展示与播放入口·实挂双锚点(music-POS-024)。

定位口径说明:YAML 的 testId 双锚(netease_private_roaming_card/play_button)
属语义树定位,运行时禁用(规范);改走 [OCR] 文本锚,播放钮为图标 OCR 不稳,
B 口径=卡片文本锚+卡带内「播放」字形探测,失败留模板标定提示。

步骤→AW 映射:
  1. 定位私享漫游卡 → open_platform_home('netease') + scroll_to_text
     ('私人漫游')(KB:私人漫游卡,域内唯一平台卡)
  2. 播放按钮可达 → ocr_scan_page 卡带内「播放」字形/文本探测
  3. 点击播放发起 → tap 卡带播放钮 → 迷你播放条出现即止(不做音频内容
     断言) → find_image(SWAN_BOTTOM_PLAYER_BAR)

cleanup: 停止播放并退出播放态——播放态收束未标定,由框架每用例冷启动
复位(不落破坏性操作)。
B 标定说明:私享漫游卡播放钮 [图] 模板与迷你播放条播放态锚待真机补截;
注:底栏播放条模板为无会话态截样,rig 持久播放会话下内容偏离可能致模板
漏配(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_BOTTOM_PLAYER_BAR


class TestMusicPos024PrivateRoamingCardPlay(BaseTest):
    """网易云私享漫游卡展示,播放按钮可达,点击播放发起。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_private_roaming_card_play_entry(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:定位私享漫游卡
        self.userA.open_platform_home("netease")
        self.userA.scroll_to_text("私人漫游")
        # 步骤 2:卡带内播放按钮可达(OCR 字形/文本探测)
        items = self.userA.ocr_scan_page()
        card = None
        for it in items:
            if "私人漫游" in it["text"]:
                card = it
                break
        assert card is not None, "私享漫游卡 [OCR] 消失(页面跳变)"
        play = None
        for it in items:
            text = it["text"].strip()
            if it["bbox"][1] < card["bbox"][1]:
                continue
            if text in ("播放", "▶", "play", "Play") or "播放" in text:
                play = it
                break
        assert play is not None, (
            "私享漫游卡未扫到播放按钮文本项(播放钮为图标 OCR 不稳;"
            "[图] 模板待补截,见 package_report.json template_needs)")
        # 步骤 3:点击播放发起(迷你播放条出现即止,不做音频内容断言)
        self.userA.tap(play["cx"], play["cy"])
        assert self.userA.find_image(SWAN_BOTTOM_PLAYER_BAR, timeout=8) \
            is not None, (
            "点击播放后迷你播放条未出现(模板未命中;播放态锚待真机标定,"
            "见 package_report.json template_needs)")
        self.userA.assert_no_auth_error()
