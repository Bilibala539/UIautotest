# CASE-ID: video-NEG-006
"""Swan 回归·M18 视频与投屏:卡片连点冷却守卫(video-NEG-006)。

用例 -> AW 映射:
- 步骤1 分类页快速双击同一 MV 卡片(连点) -> first_video_card_title 读
  运行时标题 -> tap_video_card_twice:同一坐标连续两次 tap
- 步骤2 冷却窗内第二次点击被吞(转场动画期防重复入栈) -> 以结果态承载:
  双击后按一次返回即落回分类页(exit_video_player_restore_check:竖屏
  恢复 + 六 Tab 锚 [OCR] 命中)——若冷却失效会双重入栈,单次返回仍在
  播放页,该锚即失守,守卫断言成立
- 步骤3 冷却窗外再次点击正常进播放页 -> tap_video_card(正常单次)
- 步骤4 返回退出恢复竖屏 -> exit_video_player_restore_check(禁区 4)
备注:YAML"转场动画期连续点击"以同坐标双击近似转场期补点;转场精确
时序(毫秒级窗口)不在 UI 轨,notes 登记。
禁区围栏:本机播放,不触发投屏(禁区 1)。
状态条件用例:QQ 未授权自动 skip(同 video-POS-001 口径)。
cleanup:exit_video_player_restore_check 承载。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestVideoCardCooldown(SwanRP10Mixin, BaseTest):
    """卡片连点冷却:双击不双重入栈,冷却外正常(video-NEG-006)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_video_card_double_tap_cooldown(self):
        """双击卡片仅入播放页一次(单返回即回分类页),再点正常。"""
        self.userA.ensure_logged_in_on_home()
        if not self.userA.open_qq_video_classify():
            pytest.skip("QQ 音乐未授权(平台页未授权行 [图]/授权门禁弹层命中)"
                        "——视频域用例需已授权态;授权域搁置中(2026-10-13 拍板)")
        title = self.userA.assert_video_list_loaded()
        self.userA.tap_video_card_twice(title)  # 转场期近似连点
        # 冷却守卫:双击后单次返回即回分类页(双重入栈则锚失守)
        self.userA.exit_video_player_restore_check()
        self.userA.tap_video_card(title)  # 冷却窗外正常进播放页
        self.userA.exit_video_player_restore_check()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
