# CASE-ID: library-NEG-028
"""Swan 回归·M12 收藏与曲库：聚合创建快速操作不跳过来源弹层（library-NEG-028，ADD1 复审改判 B 转，部分转换）。

用例 → AW 映射：
- S1-S2 基线（正常节奏）：create_composite_playlist——保存后来源选择
  弹层必现（方法内断言 完成/添加歌单 命中）→ 完成 → 聚合可见。
- S5 弹窗存续期断言：创建弹窗 → 关联 → 输入（不保存）→ 断言来源弹层
  未提前拉起（完成/添加歌单均未命中），关闭弹窗丢弃未保存输入。
- S3-S4 降级注记：保存点击后 200ms 内立即点击弹窗外/系统返回的快速
  破坏节奏，OCR 探测-点击周期（~1s）不可达（单次点击后到下一次操作
  间隔远超 200ms），近似近似无效（返回键会关闭已拉起弹层而非复现
  竞态），未纳入自动化——能力缺口：框架无亚秒级双操作并发编排，
  见 package_report.notes。
清理：S1-S2 产物聚合歌单经编辑弹层确认删除。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin

AGG = 'TESTSYN快操聚合'
OBSERVE = 'TESTSYN快操观察名'


class TestLibraryNeg028CompositeQuickOpSheet(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """聚合创建快速操作：保存前来源弹层不提前拉起，保存后弹层必现。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_composite_quick_op_source_sheet(self):
        """基线保存后来源弹层必现；弹窗存续期（未保存）来源弹层不拉起。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S5：弹窗存续期——输入未保存，来源弹层不得提前拉起
        self.userA.open_create_playlist_dialog()
        self.userA.click_text('关联', timeout=5)
        self.userA.input_text(OBSERVE)
        assert self.userA.probe_any_text(('完成', '添加歌单'), timeout_each=2) is None, (
            "保存前来源弹层提前拉起（快速操作守卫失守）")
        self.userA.close_create_dialog()
        # S1-S2：基线正常节奏——保存后来源弹层必现（方法内断言）
        self.userA.create_composite_playlist(AGG)
        # 清理：一次性聚合数据确认删除
        self.userA.open_composite_detail(AGG)
        self.userA.composite_delete_to_confirm()
        self.userA.composite_delete_confirm(AGG)

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例体内已含确定性清理）。"""
        pass
