# CASE-ID: radio-POS-010
"""Swan 回归·电台：分类切换 reset 加载与终态一致（radio-POS-010 正向面）。

步骤 -> AW 映射（selectType reset 加载 + _loadGeneration 代次隔离；
坑 7 正向面：代次隔离护渲染，终态与最后选中分类一致）：
- 步骤1 「全部」分类下记录列表内容集 -> ocr_page_texts 基线；
- 步骤2 快速切换至另一具体分类 -> click_any_text（分类名由
  broadcast/type 动态返回，常见分类文案候选兜底，中文未核准登记
  template_needs），列表 reset：内容集与「全部」态出现变化；
- 步骤3 连切第二个分类 -> 终态内容集再次随最后选中分类刷新
  （无混排由代次隔离契约承担，OCR 侧断内容集变化）；
- 收尾 切回「全部」。

清理：纯查询（会话内切回全部），teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadioCategorySwitch(BaseTest):
    """radio-POS-010：切分类列表重置，连切终态随最后选中刷新。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_category_switch_reset(self):
        """切分类触发列表重置，连切终态一致。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        self.userA.tap_card_by_texts("全国电台", "国家台", "全国")
        self.userA.assert_any_of_texts("全部", timeout=10)
        # 步骤1：「全部」态列表内容基线
        all_texts = [t for t in self.userA.ocr_page_texts() if len(t) >= 4]
        # 步骤2：切换到另一具体分类，列表 reset（内容集变化）
        self.userA.click_any_text("音乐", "情感", "脱口秀", "相声", "新闻",
                                  timeout=6)
        switched = [t for t in self.userA.ocr_page_texts() if len(t) >= 4]
        assert switched != all_texts, "切分类后列表未重置"
        # 步骤3：连切第二个分类，终态随最后选中刷新
        self.userA.click_any_text("情感", "脱口秀", "相声", "新闻", "音乐",
                                  timeout=6)
        final = [t for t in self.userA.ocr_page_texts() if len(t) >= 4]
        assert final != switched, "连切后终态未随最后选中分类刷新"
        # 收尾：切回「全部」
        self.userA.click_any_text("全部", timeout=6)

    def teardown(self) -> None:
        """纯查询无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
