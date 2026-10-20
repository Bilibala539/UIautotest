# CASE-ID: library-NEG-026
"""Swan 回归·M12 收藏与曲库：改名中断与黑屏链（library-NEG-026，ADD1 复审改判 B 转，部分转换）。

用例 → AW 映射：
- S1-S2 本地歌单改名中断：详情更多菜单 → 改名弹窗 → 清空输入半段新名
  → 系统返回键退出不保存 → 断言弹窗已收、列表/详情仍为原名。
- S3-S4 聚合改名提交后立即返回：composite_rename 完整提交（新名详情
  回显）→ 紧接 press_back → 歌单列表见新名（提交不因立即返回丢失）。
- S6 终态一致性：重进聚合详情 → 详情头新名 + 聚合段列表新名一致。
- S4-S5 黑屏观察段（500ms pop 窗口内黑屏/自恢复）：视觉面 + 亚秒窗口
  OCR 探测周期不可达（单次 OCR ~1s），未纳入自动化，见
  package_report.notes（能力缺口：框架无亚秒级转场采样通道）。
降级注记：S2 输入"一半"以半段字符串承载；改名字段聚焦由 clear_input
（点入清空）承载。清理：本地与聚合一次性数据经确认删除。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin
from image.image_name_mapping import SWAN_PD_MORE_BTN

LOCAL = 'TESTSYN中断R0'
PARTIAL = 'TESTSYN中断-前半'
AGG = 'TESTSYN中断聚合'
AGG_R2 = 'TESTSYN中断聚合R2'


class TestLibraryNeg026RenameInterruptChain(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """改名中断与黑屏链：本地改名返回不保存，聚合改名提交后立即返回不丢。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_rename_interrupt_and_blackout_chain(self):
        """本地改名中断保持原名；聚合改名提交后立即返回仍生效。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1-S2：本地歌单改名中断（输入半段 → 返回键不保存 → 原名不变）
        self.userA.create_local_playlist(LOCAL)
        self.userA.open_playlist_detail('swan', LOCAL)
        self.userA.click_image(SWAN_PD_MORE_BTN, timeout=5)
        self.userA.click_text_candidates(('改名', '重命名'), timeout_each=3)
        self.userA.clear_input()
        self.userA.input_text(PARTIAL)
        self.userA.press_back()
        assert self.userA.find_text_by_ocr(LOCAL, timeout=8) is not None, (
            "改名中断退出后原名不可见（可能误保存或列表未回）")
        # S3-S4：聚合改名提交后立即返回（提交不丢失）
        self.userA.create_composite_playlist(AGG)
        self.userA.composite_rename(AGG_R2)
        self.userA.press_back()
        self.userA.assert_any_text((AGG_R2,), timeout=8)
        # S6：重进详情，列表与详情头新名一致
        self.userA.open_composite_detail(AGG_R2)
        assert self.userA.find_text_by_ocr(AGG_R2, timeout=8) is not None, (
            "重进聚合详情未见新名（终态不一致）")
        # 清理：聚合与本地一次性数据确认删除
        self.userA.composite_delete_to_confirm()
        self.userA.composite_delete_confirm(AGG_R2)
        self.userA.press_back()
        self.userA.open_home_card('歌单')
        self.userA.open_playlist_detail('swan', LOCAL)
        self.userA.delete_playlist_via_detail_menu(LOCAL)

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例体内已含确定性清理）。"""
        pass
