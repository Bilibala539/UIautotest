# CASE-ID: video-POS-004
"""Swan 回归·M18 视频与投屏:视频搜索态与双态数据源切换(video-POS-004)。

用例 -> AW 映射:
- 步骤1 点击搜索条输入关键词(防抖 GET music/search type=10) ->
  open_video_search:搜索条 [OCR] 点击 -> input_text -> 结果标题命中
  关键词 [OCR] 为搜索态数据源已切换的证据(防抖为服务端行为)
- 步骤2 校验搜索结果列表 -> 关键词 [OCR] 命中断言(同上)
- 步骤3 搜索态下 Tab/投放入口显隐(坑 13:与分类态不同轨,记录表现
  不判值) -> 观察式,不做硬断言(坑 13 纪律:表现不判值),notes 登记
- 步骤4 清空关键词返回分类态 -> clear_video_search:clear_input 后
  六 Tab 条 [OCR] 重新命中(数据源切回分类态)
关键词按 YAML data 口径取必有结果热词,执行轮可校准(值直接内联)。
状态条件用例:QQ 未授权自动 skip(同 video-POS-001 口径)。
cleanup:清空搜索词返回分类态(clear_video_search 承载)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestVideoSearchMode(SwanRP10Mixin, BaseTest):
    """视频搜索态:type=10 防抖与双态数据源切换(video-POS-004)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_video_search_mode_switch(self):
        """搜索态出结果,清空关键词后数据源切回分类态(六 Tab 回归)。"""
        self.userA.ensure_logged_in_on_home()
        if not self.userA.open_qq_video_classify():
            pytest.skip("QQ 音乐未授权(平台页未授权行 [图]/授权门禁弹层命中)"
                        "——视频域用例需已授权态;授权域搁置中(2026-10-13 拍板)")
        self.userA.open_video_search('周杰伦')
        # 步骤3 显隐分轨为观察式(坑 13 表现不判值):不判 Tab/投放具体显隐
        self.userA.clear_video_search()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
