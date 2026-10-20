# CASE-ID: video-POS-008
"""Swan 回归·M18 视频与投屏:投放弹层与设备过滤(video-POS-008)。

用例 -> AW 映射:
- 步骤1 分类页点击右上「投放」按钮 -> open_cast_sheet:「投放」[OCR]
  定位点击(只开不选,M18 禁区 1),弹层锚文案 [OCR] 命中即弹层已开
- 步骤2 校验弹层渲染(标题/说明文案) -> 弹层锚文案 [OCR] 命中为最小
  断言;标题/空态专属文案待执行轮校准(notes/template_needs 登记)
- 步骤3 混合设备过滤(仅本机支持协议的设备) -> 依赖在线 screen 设备池
  (设备 00c)预置异构设备,离线执行器无法构造,设备侧分轨,notes 登记
- 步骤4 返回关闭弹层,无残留投屏请求 -> dismiss_cast_sheet_check_route:
  press_back 关弹层 + 落回分类页锚 [OCR] 复核(返回路由而非遮罩误触)
禁区围栏:只打开弹层并返回关闭,绝不点击任何设备条目(禁区 1)。
状态条件用例:QQ 未授权自动 skip(同 video-POS-001 口径)。
cleanup:dismiss_cast_sheet_check_route 承载(关弹层+回分类页)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestVideoCastSheet(SwanRP10Mixin, BaseTest):
    """投放弹层空态:开/关与返回路由(video-POS-008)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_video_cast_sheet_open_close(self):
        """「投放」开弹层见锚文案,返回关闭落回分类页且路由正确。"""
        self.userA.ensure_logged_in_on_home()
        if not self.userA.open_qq_video_classify():
            pytest.skip("QQ 音乐未授权(平台页未授权行 [图]/授权门禁弹层命中)"
                        "——视频域用例需已授权态;授权域搁置中(2026-10-13 拍板)")
        anchor = self.userA.open_cast_sheet()
        # 步骤2 弹层渲染以锚文案命中承载;专属标题/空态文案待校准登记
        assert anchor, "投放弹层未命中任何锚文案(完成/取消/本地)"
        self.userA.dismiss_cast_sheet_check_route()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
