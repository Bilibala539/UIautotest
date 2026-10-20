# CASE-ID: video-POS-007
"""Swan 回归·M18 视频与投屏:进横屏退竖屏与播放链路(video-POS-007)。

用例 -> AW 映射:
- 步骤1 分类页点击 MV 卡片(统一入口收口) -> first_video_card_title 读
  运行时标题 -> tap_video_card:标题 [OCR] 定位点击
- 步骤2 播放页强制横屏(方向协调器 enterLandscape) -> 进页后截图宽>高
  断言,即横屏已被强制生效的可观察证据
- 步骤3 返回退出播放页,恢复竖屏(M18 禁区 4:退出后须回到一级页竖屏)
  -> exit_video_player_restore_check:press_back + 截图高>宽断言 +
  分类页六 Tab 锚 [OCR] 复核
- 步骤4 旋转链路(重力/悬浮窗/16+ ageRating 渠道差异) -> 依赖系统旋转
  控制与渠道包差异,不在单 App UI 轨,notes/template_needs 登记
禁区围栏:本机播放,不触发投屏(M18 禁区 1);核心断言为"进横退竖"。
状态条件用例:QQ 未授权自动 skip(同 video-POS-001 口径)。
cleanup:exit_video_player_restore_check 承载(退出+竖屏核对)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestVideoLandscapeRestore(SwanRP10Mixin, BaseTest):
    """进横屏退竖屏:方向协调器进出一致性(video-POS-007)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_video_enter_landscape_exit_portrait(self):
        """点播进播放页横屏,退出恢复竖屏并落回分类页(禁区 4)。"""
        self.userA.ensure_logged_in_on_home()
        if not self.userA.open_qq_video_classify():
            pytest.skip("QQ 音乐未授权(平台页未授权行 [图]/授权门禁弹层命中)"
                        "——视频域用例需已授权态;授权域搁置中(2026-10-13 拍板)")
        title = self.userA.assert_video_list_loaded()
        self.userA.tap_video_card(title)  # 进页断言横屏(宽>高)
        self.userA.exit_video_player_restore_check()  # 退出断言竖屏(高>宽)

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
