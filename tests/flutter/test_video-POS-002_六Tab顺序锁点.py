# CASE-ID: video-POS-002
"""Swan 回归·M18 视频与投屏:六固定 Tab 顺序与 id 映射(video-POS-002)。

用例 -> AW 映射:
- 步骤1 打开分类页读取 Tab 条全序列(推荐 id=0/内地 12/韩国 9/港台 13/
  日本 8/欧美 3) -> assert_video_tab_order:逐 Tab [OCR] 定位并断言 x
  坐标严格递增(顺序断言与末两项「日本/欧美」锁点同法承载)
- 步骤2 专项断言末两项必须日本、欧美 -> 序列尾部两参数即锁点
- 步骤3 逐 Tab 点击切换、列表随 type 刷新 -> cycle_video_tabs:每 Tab
  点击后以卡片标题 [OCR] 可读为列表刷新证据
- 步骤4 Tab 文案随语言切换(l10n 六 key) -> 须系统设置外部改语言,
  超出单 App UI 轨,已登记 notes
状态条件用例:QQ 未授权自动 skip(同 video-POS-001 口径)。
cleanup:返回推荐 Tab(cycle_video_tabs('推荐'))。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestVideoTabOrder(SwanRP10Mixin, BaseTest):
    """六固定 Tab 顺序与 id 映射(video-POS-002)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_video_tab_order_and_id_mapping(self):
        """六 Tab 序推荐/内地/韩国/港台/日本/欧美,末两项日本欧美锁点。"""
        self.userA.ensure_logged_in_on_home()
        if not self.userA.open_qq_video_classify():
            pytest.skip("QQ 音乐未授权(平台页未授权行 [图]/授权门禁弹层命中)"
                        "——视频域用例需已授权态;授权域搁置中(2026-10-13 拍板)")
        self.userA.assert_video_tab_order('推荐', '内地', '韩国', '港台',
                                          '日本', '欧美')
        self.userA.cycle_video_tabs('推荐', '内地', '韩国', '港台',
                                    '日本', '欧美')
        self.userA.cycle_video_tabs('推荐')  # cleanup:返回推荐 Tab

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
