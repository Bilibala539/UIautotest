# CASE-ID: video-NEG-012
"""Swan 回归·M18 视频与投屏:退出方向恢复与进程回收零崩溃(video-NEG-012)。

用例 -> AW 映射:
- 步骤1 横屏播放中正常返回退出视频页 -> open_qq_video_classify(未授权条件
  skip) -> assert_video_list_loaded + tap_video_card(横屏落页断言) ->
  exit_video_player_restore_check:press_back + 竖屏恢复断言 + 落回分类页锚
  [OCR](三重恢复的 UI 面:竖屏+一级页)
- 步骤3 视频页进程被杀(系统回收)后回一级页 -> 再点播进横屏播放页 ->
  relaunch_app(杀进程后冷启动,等待落地页锚)模拟进程回收 -> assert_on_home
  (落回一级首页,零崩溃可恢复;横屏残留为系统现状按坑 10 不判值)
- 步骤2 自动旋转期内旋转设备(竖->横->竖) -> 需屏幕方向/传感器控制通道,
  框架无此能力,分轨登记 notes
- 步骤4 Android 16+ 原生通道对照 -> 日志/跨壳面,分轨登记 notes
禁区围栏(M18 禁区 4):收尾一级页竖屏铁律由步骤1 的竖屏断言承载;进程回收
路径落首页壳锚。状态条件用例:QQ 未授权自动 skip(同 video-POS-001 口径)。
cleanup:冷启动模型承担(App 状态由夹具重置,无用例私有清理)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestVideoExitRestoreRecycle(SwanRP10Mixin, BaseTest):
    """退出方向恢复守卫与进程回收可恢复(video-NEG-012)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_video_exit_restore_and_recycle(self):
        """正常退出三重恢复;进程回收后冷启动落一级页零崩溃。"""
        self.userA.ensure_logged_in_on_home()
        if not self.userA.open_qq_video_classify():
            pytest.skip("QQ 音乐未授权(平台页未授权行 [图]/授权门禁弹层命中)"
                        "——视频域用例需已授权态;授权域搁置中(2026-10-13 拍板)")
        # 步骤1 横屏进 -> 正常返回 -> 竖屏恢复 + 落回分类页
        title = self.userA.assert_video_list_loaded()
        self.userA.tap_video_card(title)
        self.userA.exit_video_player_restore_check()
        # 步骤3 进程回收(杀进程冷启动模拟)后回一级页,零崩溃可恢复
        self.userA.tap_video_card(title)
        self.userA.relaunch_app(self.userA.package)
        self.userA.assert_on_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
