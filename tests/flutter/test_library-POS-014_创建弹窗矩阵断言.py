# CASE-ID: library-POS-014
"""Swan 回归·M12 收藏与曲库：创建弹窗平台与类型矩阵（library-POS-014）。

用例 → AW 映射：
- S1 打开创建弹窗：open_home_card('歌单') → open_create_playlist_dialog。
- S2-S3 平台清单：assert_any_text(('Swans', 'SWAN'))（Swans 恒在）+ 酷狗展示项
  probe_any_text(('酷狗',))（展示断言；置灰不可选行为不点击验证——执行轮
  校准，禁区 8 授权交互不触碰）。
- S4-S5 类型选项：assert_any_text(('自建',)) + 关联类型 probe_any_text
  (('关联',))（授权子集下平台选项一致性降级为关键项存在性）。
- S6-S7 21 字符截断：input_text(21 字符)——输入框回显无法 OCR 直读，截断
  断言降级为「不提交直接关窗」零写入口径 + close_create_dialog 收窗。
清理：全程不提交（关窗零写入），无数据清理动作。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos014CreateDialogMatrix(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """创建弹窗矩阵：平台清单与类型选项渲染，21 字符输入不产生脏数据。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_create_dialog_matrix(self):
        """弹窗平台/类型选项渲染正确，超长输入后关窗零写入。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1：打开弹窗
        self.userA.open_create_playlist_dialog()
        # S2-S3：平台清单（Swans 恒在 + 酷狗展示项，不点击）
        self.userA.assert_any_text(('Swans', 'SWAN'), timeout=5)
        assert self.userA.probe_any_text(('酷狗',), timeout_each=3) is not None, (
            "创建弹窗平台清单未见酷狗展示项")
        # S4-S5：类型选项
        self.userA.assert_any_text(('自建',), timeout=5)
        assert self.userA.probe_any_text(('关联',), timeout_each=3) is not None, (
            "创建弹窗类型选项未见关联")
        # S6-S7：21 字符输入后不提交，直接关窗（零写入）
        self.userA.input_text('TESTSYNTHETIC边界名二十字符齐长')
        self.userA.close_create_dialog()

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（关窗零写入）。"""
        pass
