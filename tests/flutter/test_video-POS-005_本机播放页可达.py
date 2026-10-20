# CASE-ID: video-POS-005
"""Swan 回归·M18 视频与投屏:本机播放页可达与元素渲染(video-POS-005)。

用例 -> AW 映射:
- 步骤1 分类列表点击任一 MV 卡片(统一入口收口) -> first_video_card_title
  读运行时标题 -> tap_video_card:标题 [OCR] 定位点击
- 步骤2 校验播放页元素(标题/艺术家渲染,本机播放器出画面) ->
  播放页强制横屏(方向协调器 enterLandscape),截图宽>高断言即"播放页
  已开+本机播放器创建"的可观察证据;卡片标题 [OCR] 在播放页命中
- 步骤3 校验本机播放控制条(播放/暂停控件可见) -> 视频播放页控件
  模板未截取注册,不在本轨硬断言,template_needs 登记
- 步骤4 返回退出播放页 -> exit_video_player_restore_check:press_back +
  竖屏恢复断言(M18 禁区 4 收尾铁律)+ 落回分类页
禁区围栏:本用例为本机播放(允许),不触发任何投屏连接(M18 禁区 1)。
状态条件用例:QQ 未授权自动 skip(同 video-POS-001 口径)。
cleanup:exit_video_player_restore_check 承载(退出+竖屏核对)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestVideoLocalPlayback(SwanRP10Mixin, BaseTest):
    """本机播放页可达与元素渲染(非投屏态)(video-POS-005)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_video_local_playback_page(self):
        """点播 MV 卡片进本机播放页(横屏),退出恢复竖屏回分类页。"""
        self.userA.ensure_logged_in_on_home()
        if not self.userA.open_qq_video_classify():
            pytest.skip("QQ 音乐未授权(平台页未授权行 [图]/授权门禁弹层命中)"
                        "——视频域用例需已授权态;授权域搁置中(2026-10-13 拍板)")
        title = self.userA.assert_video_list_loaded()
        self.userA.tap_video_card(title)
        # 播放页元素:标题随横屏页渲染(标题 [OCR] 命中);控制条模板待截
        assert self.userA.find_text_by_ocr(title, timeout=10) is not None, (
            "播放页未见到所播 MV 标题 [OCR]")
        self.userA.exit_video_player_restore_check()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
