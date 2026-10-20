# CASE-ID: music-POS-059
"""Swan 回归·M07 QQ音乐:跨平台主页保活(music-POS-059)。

步骤→AW 映射(7.2 QQ音乐,KeepAlive 上下文保持,全程只读):
  1. QQ 主页滚动至「音乐雷达」区块(保活位置标记,KB 区块序中位)→
     press_back 条件回平台页(平台主页=子级页 1 次返回,KB 同构网易云)
  2. 回平台页再进网易云主页 → 再回再进酷狗主页(open_platform_home
     内含授权态闸门,缺失行 skip=YAML SKIP-NO-ITEM)
  3. 再进 QQ 主页 → 「音乐雷达」仍可见=滚动位置保持(KeepAlive 生效;
     若页面回顶则保活丢失)
  4. 底栏播放条观察(若存在在播内容;不点击不切换)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:「音乐雷达」为 QQ 主页中位区块锚(KB 区块序),服务端
区块轮换或主页顶栏锚改版时以显式断言暴露;三主页 KeepAlive 无新增
模板需求。每级返回后断言平台页锚,防根级盲返。
"""

from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_BOTTOM_PLAYER_BAR


class TestMusicPos059CrossPlatformKeepalive(BaseTest):
    """三平台主页跨切上下文保持,保活页状态恢复。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_cross_platform_keepalive(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:QQ 主页滚动至「音乐雷达」→ 条件回平台页
        self.userA.open_platform_home("qq")
        self.userA.scroll_to_text("音乐雷达")
        self.userA.press_back()  # 平台主页=子级页,1 次回平台页
        assert self.userA.find_text_by_ocr("网易云音乐", timeout=6) is not None, (
            "QQ 主页返回后未到达平台入口页(返回栈异常)")
        # 步骤 2:网易云主页 → 回平台页 → 酷狗主页
        self.userA.open_platform_home("netease")
        self.userA.press_back()
        assert self.userA.find_text_by_ocr("酷狗音乐", timeout=6) is not None, (
            "网易云主页返回后未到达平台入口页(返回栈异常)")
        self.userA.open_platform_home("kugou")
        self.userA.press_back()
        assert self.userA.find_text_by_ocr("QQ音乐", timeout=6) is not None, (
            "酷狗主页返回后未到达平台入口页(返回栈异常)")
        # 步骤 4:底栏播放条观察(若存在在播内容;不点击不切换)
        self.userA.find_image(SWAN_BOTTOM_PLAYER_BAR, timeout=3)
        # 步骤 3:再进 QQ 主页,滚动位置保持(「音乐雷达」仍可见=未回顶)
        self.userA.open_platform_home("qq")
        assert self.userA.find_text_by_ocr("音乐雷达", timeout=8) is not None, (
            "QQ 主页再次进入未保持滚动位置(「音乐雷达」不可见=KeepAlive "
            "丢失或服务端区块轮换)")
