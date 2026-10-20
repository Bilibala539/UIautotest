# CASE-ID: video-NEG-014
"""Swan 回归·M18 视频与投屏:搜索态点播同链收口(video-NEG-014)。

用例 -> AW 映射:
- 步骤2 分类页切搜索态输入关键词 -> open_qq_video_classify(未授权条件 skip)
  -> open_video_search('周杰伦')(防抖请求回结果,搜索态数据源切换 [OCR] 证据)
- 步骤3 搜索态选 MV 点播 -> assert_video_list_loaded(搜索结果首卡标题,运行时
  数据) -> tap_video_card(横屏落页=同一 PlatformVideoPlaybackLauncher 入口
  收口证据) -> press_back + 竖屏恢复(M18 禁区 4 收尾铁律) -> clear_video_search
  (清关键词回分类态,Tab 锚 [OCR])
- 步骤1 投屏态播放页进度来源(UPnP 轮询) -> 需受控投屏会话在播(真实第二
  设备),框架无多机编排通道,分轨登记 notes
禁区围栏(M18 禁区 4):退出播放页后竖屏恢复 + 回分类态;状态条件用例:
QQ 未授权自动 skip(同 video-POS-001 口径)。
cleanup:clear_video_search 承载(清空搜索态回分类页)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestVideoSearchTapSameLauncher(SwanRP10Mixin, BaseTest):
    """搜索态切数据源且点播同 launcher 收口(video-NEG-014)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_video_search_tap_same_launcher(self):
        """搜索态出结果可点播进同一播放页,退出竖屏恢复清搜索态。"""
        self.userA.ensure_logged_in_on_home()
        if not self.userA.open_qq_video_classify():
            pytest.skip("QQ 音乐未授权(平台页未授权行 [图]/授权门禁弹层命中)"
                        "——视频域用例需已授权态;授权域搁置中(2026-10-13 拍板)")
        # 步骤2 搜索态数据源切换
        self.userA.open_video_search('周杰伦')
        # 步骤3 搜索态选 MV 点播:同一 launcher 收口(横屏播放页落页)
        title = self.userA.assert_video_list_loaded()
        self.userA.tap_video_card(title)
        # M18 禁区 4 收尾铁律:退出播放页竖屏恢复,再清搜索态回分类页
        self.userA.press_back()
        self.userA.assert_portrait_orientation()
        self.userA.clear_video_search()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
