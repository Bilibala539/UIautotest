# CASE-ID: video-POS-001
"""Swan 回归·M18 视频与投屏:视频分类页可达四要素(video-POS-001)。

用例 -> AW 映射:
- 步骤1 从音乐平台域打开 QQ 视频分类页 -> open_qq_video_classify
  (平台 tab [图] -> QQ 行 [OCR] -> 授权门禁探针 -> QQ 主页锚 [OCR] ->
  「视频」入口 [OCR] -> 分类页 Tab 锚 [OCR])
- 步骤2 返回键语义标签(platform_video_classify_back,M18 全域唯一显式
  语义标签) -> 运行时禁语义 key,以 press_back 可退出 push 页承载返回
  可用性(退出竖屏铁律归 video-POS-007/exit_video_player_restore_check)
- 步骤3 搜索条与六 Tab 条渲染 -> assert_video_search_bar +
  assert_video_tab_order(x 严格递增即顺序正确)
- 步骤4 MV 列表非空与投放入口可见 -> assert_video_list_loaded +
  「投放」[OCR] 存在断言(只断言不点击,M18 禁区 1)

状态条件用例:QQ 音乐未授权时授权门禁拦截,自动 pytest.skip(与既有
平台内容页样例同口径);授权后自动恢复运行。
cleanup:press_back 返回平台域 -> go_home。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestVideoClassifyPageReachable(SwanRP10Mixin, BaseTest):
    """视频分类页可达:返回/搜索条/Tab/列表四要素(video-POS-001)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_video_classify_page_reachable(self):
        """QQ 视频分类页打开,搜索条/六 Tab/列表/投放入口四要素齐备。"""
        self.userA.ensure_logged_in_on_home()
        if not self.userA.open_qq_video_classify():
            pytest.skip("QQ 音乐未授权(平台页未授权行 [图]/授权门禁弹层命中)"
                        "——视频域用例需已授权态;授权域搁置中(2026-10-13 拍板)")
        self.userA.assert_video_search_bar()
        self.userA.assert_video_tab_order('推荐', '内地', '韩国', '港台',
                                          '日本', '欧美')
        self.userA.assert_video_list_loaded()
        assert self.userA.find_text_by_ocr("投放", timeout=5) is not None, (
            "分类页右上角投放入口「投放」[OCR] 不可见")
        self.userA.press_back()  # 分类页为 push 页,返回平台域
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
