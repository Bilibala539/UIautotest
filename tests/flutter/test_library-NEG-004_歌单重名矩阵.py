# CASE-ID: library-NEG-004
"""Swan 回归·M12 收藏与曲库：歌单重名矩阵（library-NEG-004，ADD1 复审改判 B 转）。

用例 → AW 映射：
- 前置：自建基线本地歌单 + 两个聚合对照歌单（create_local_playlist /
  create_composite_playlist，自有一次性 TESTSYN 数据；每次创建前回首页
  再进歌单卡，保证弹窗在 Swans 段拉起）。
- S1 本地重名再创建：创建弹窗重输基线名保存 → 现状断言（允许或拒绝
  记录其一，双分支）：弹窗驻留/已存在提示 = 拒绝分支；弹窗已收且列表
  见名 = 允许分支（允许分支随后把一行改名区隔，供清理逐一删除）。
- S2 聚合重名创建预检：创建弹窗 → 关联 → 重输 C1 名保存 → 断言来源
  弹层未拉起（完成/添加歌单均未命中）且弹窗/提示仍在（预检拦截）。
- S3 改名撞名预检：C2 编辑弹层 → 改名 → 重输 C1 名保存 → 断言改名
  弹窗驻留（改名/已存在命中）；返回两层后详情头仍为原名（新名未生效）。
- S4 变体口径（前后空格差异）：输入框内容读取无通道（禁 OCR 读框），
  未纳入自动化，见 package_report.notes。
清理（用例体内，状态确定）：聚合 C2/C1 经编辑弹层确认删除；本地
ALT/BASE 经详情菜单删除。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin

BASE = 'TESTSYN重名基准A'
ALT = 'TESTSYN重名基准B'
C1 = 'TESTSYN重名对照C1'
C2 = 'TESTSYN重名对照C2'


class TestLibraryNeg004DuplicateNameMatrix(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """歌单重名矩阵：本地重名现状断言 + 聚合创建/改名重名预检拦截。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_duplicate_name_matrix(self):
        """本地重名创建现状断言；聚合重名创建与改名被预检拦截。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1：基线本地歌单 + 本地重名再创建（现状断言双分支）
        self.userA.create_local_playlist(BASE)
        self.userA.open_create_playlist_dialog()
        self.userA.input_text(BASE)
        self.userA.click_text_candidates(('保存', '确定'), timeout_each=3)
        s1_allowed = self.userA.probe_any_text(
            ('已存在', '重名', '创建歌单', '歌单名称'), timeout_each=2) is None
        if s1_allowed:
            assert self.userA.find_text_by_ocr(BASE, timeout=8) is not None, (
                "允许分支：弹窗已收但列表未见重名歌单")
            # 允许分支产生重名两行：把最上行改名区隔，供清理逐一删除
            self.userA.open_playlist_detail('swan', BASE)
            self.userA.rename_playlist_via_menu(ALT)
            self.userA.press_back()
        else:
            if self.userA.probe_any_text(('取消', '关闭'), timeout_each=2) is not None:
                self.userA.close_create_dialog()
        # S2：聚合重名创建预检（重输 C1 名）
        self.userA.press_back()
        self.userA.open_home_card('歌单')
        self.userA.create_composite_playlist(C1)
        self.userA.press_back()
        self.userA.open_home_card('歌单')
        self.userA.create_composite_playlist(C2)
        self.userA.press_back()
        self.userA.open_home_card('歌单')
        self.userA.open_create_playlist_dialog()
        self.userA.click_text('关联', timeout=5)
        self.userA.input_text(C1)
        self.userA.click_text_candidates(('保存', '确定'), timeout_each=3)
        assert self.userA.probe_any_text(('完成', '添加歌单'), timeout_each=3) is None, (
            "重名聚合仍拉起来源弹层（预检未拦截）")
        assert self.userA.probe_any_text(
            ('已存在', '重名', '创建歌单', '歌单名称', '取消'), timeout_each=3) is not None, (
            "重名聚合预检拦截后既无提示也无弹窗驻留")
        if self.userA.probe_any_text(('创建歌单', '歌单名称', '取消'), timeout_each=2) is not None:
            self.userA.close_create_dialog()
        # S3：聚合改名撞名预检（C2 改成 C1 名）
        self.userA.open_composite_detail(C2)
        self.userA.open_composite_edit_dialog()
        self.userA.click_text('改名', timeout=5)
        self.userA.clear_input()
        self.userA.input_text(C1)
        self.userA.click_text_candidates(('保存', '确定'), timeout_each=3)
        assert self.userA.probe_any_text(
            ('改名', '已存在', '重名'), timeout_each=3) is not None, (
            "重名改名未被预检拦截（弹窗已收且未提示）")
        self.userA.press_back()
        self.userA.press_back()
        assert self.userA.find_text_by_ocr(C2, timeout=8) is not None, (
            "改名拦截后详情头未回显原名")
        # 清理：聚合 C2/C1（编辑弹层确认删除，自有一次性数据）
        self.userA.composite_delete_to_confirm()
        self.userA.composite_delete_confirm(C2)
        self.userA.open_composite_detail(C1)
        self.userA.composite_delete_to_confirm()
        self.userA.composite_delete_confirm(C1)
        # 清理：本地 ALT/BASE（详情菜单删除；拒绝分支无 ALT 行，条件删除）
        self.userA.press_back()
        self.userA.open_home_card('歌单')
        if self.userA.find_text_by_ocr(ALT, timeout=3) is not None:
            self.userA.open_playlist_detail('swan', ALT)
            self.userA.delete_playlist_via_detail_menu(ALT)
        self.userA.open_playlist_detail('swan', BASE)
        self.userA.delete_playlist_via_detail_menu(BASE)

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例体内已含确定性清理）。"""
        pass
