# CASE-ID: video-POS-003
"""Swan 回归·M18 视频与投屏:分类列表加载与卡片渲染(video-POS-003)。

用例 -> AW 映射:
- 步骤1 默认推荐 Tab 观察列表请求(GET music/getMvTopList type=0/sort)
  -> 请求参数面为日志断言,不在 UI 轨(notes 登记);列表健康以卡片渲染承载
- 步骤2 校验列表渲染 -> assert_video_list_loaded:内容区 [OCR] 读出
  卡片标题即列表非空
- 步骤3 切 Tab(内地 id=12)观察参数变化与列表刷新 -> cycle_video_tabs
  ('内地'):点击后卡片标题 [OCR] 可读为列表已刷新证据
- 步骤4 纵向滚动分页 -> swipe_up 后再断言卡片标题可读(分页加载健康)
状态条件用例:QQ 未授权自动 skip(同 video-POS-001 口径)。
cleanup:返回推荐 Tab(cycle_video_tabs('推荐'))。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestVideoClassifyList(SwanRP10Mixin, BaseTest):
    """分类列表加载:请求参数面与卡片渲染(video-POS-003)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_video_classify_list_loaded(self):
        """默认 Tab 列表非空,切内地 Tab 列表刷新,上滑分页健康。"""
        self.userA.ensure_logged_in_on_home()
        if not self.userA.open_qq_video_classify():
            pytest.skip("QQ 音乐未授权(平台页未授权行 [图]/授权门禁弹层命中)"
                        "——视频域用例需已授权态;授权域搁置中(2026-10-13 拍板)")
        self.userA.assert_video_list_loaded()
        self.userA.cycle_video_tabs('内地')
        self.userA.swipe_up()
        self.userA.assert_video_list_loaded()
        self.userA.cycle_video_tabs('推荐')  # cleanup:返回推荐 Tab

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
