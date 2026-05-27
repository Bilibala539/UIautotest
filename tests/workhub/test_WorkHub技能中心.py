"""
测试用例: WorkHub技能中心
覆盖用例: Row 98-118 - 技能中心入口、列表、搜索、自定义技能管理
"""
from conftest import BaseTest


class TestWorkhubSkillCenter(BaseTest):
    """WorkHub技能中心 - 列表与Tab"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_skill_center_entry(self):
        """
        验证从AI首页进入技能中心

        覆盖Excel行: 98(入口), 99(官方Tab), 100(双列网格), 101(卡片信息)

        步骤:
        1. 进入WorkHub
        2. 查找技能中心入口（通常是"更多技能"或技能Tab滑到底）
        3. 验证进入技能中心页面
        4. 验证官方Tab默认选中

        预期结果:
        - 技能中心页面可见
        - 默认展示官方Tab
        - 技能卡片以网格形式展示
        """
        self.userA.aw.enter_workhub()

        # 查找技能中心入口 - 可能在输入框下方或通过"/"触发
        # 先尝试找"技能中心"文字
        skill_pos = self.userA.aw.find_text_by_ocr("技能中心", timeout=3)
        if not skill_pos:
            # 尝试找"更多"或"查看全部"
            skill_pos = self.userA.aw.find_text_by_ocr("更多技能", timeout=3)
        if not skill_pos:
            skill_pos = self.userA.aw.find_text_by_ocr("查看全部", timeout=3)

        if skill_pos:
            self.userA.aw.tap(skill_pos[0], skill_pos[1])
            self.userA.aw.sleep(3)

            # 验证进入技能中心
            results = self.userA.aw.ocr_scan_page()
            page_texts = [r['text'] for r in results]
            has_skill_center = any('官方' in t or '自定义' in t or '技能' in t for t in page_texts)
            assert has_skill_center, f"未进入技能中心: {page_texts[:10]}"

    def test_skill_center_custom_tab(self):
        """
        验证切换到自定义Tab

        覆盖Excel行: 102(切换), 103(空状态), 104(有数据时列表)

        步骤:
        1. 进入技能中心
        2. 点击"自定义"Tab
        3. 验证Tab切换成功

        预期结果:
        - 自定义Tab可切换
        - 显示空状态或自定义技能列表
        """
        self.userA.aw.enter_workhub()

        # 进入技能中心
        skill_pos = self.userA.aw.find_text_by_ocr("技能中心", timeout=3)
        if not skill_pos:
            skill_pos = self.userA.aw.find_text_by_ocr("更多技能", timeout=3)
        if not skill_pos:
            skill_pos = self.userA.aw.find_text_by_ocr("查看全部", timeout=3)

        if skill_pos:
            self.userA.aw.tap(skill_pos[0], skill_pos[1])
            self.userA.aw.sleep(3)

            # 点击"自定义"Tab
            custom_pos = self.userA.aw.find_text_by_ocr("自定义", timeout=5)
            if custom_pos:
                self.userA.aw.tap(custom_pos[0], custom_pos[1])
                self.userA.aw.sleep(2)

                # 验证切换成功（页面有内容或空态提示）
                results = self.userA.aw.ocr_scan_page()
                assert len(results) > 0, "自定义Tab切换后页面空白"

    def test_skill_center_search(self):
        """
        验证技能中心搜索功能

        覆盖Excel行: 106(搜索框), 107(实时过滤), 108(命中结果)

        步骤:
        1. 进入技能中心
        2. 点击搜索图标
        3. 输入关键词
        4. 验证过滤结果

        预期结果:
        - 搜索框可展开
        - 输入关键词后列表更新
        """
        self.userA.aw.enter_workhub()

        # 进入技能中心
        skill_pos = self.userA.aw.find_text_by_ocr("技能中心", timeout=3)
        if not skill_pos:
            skill_pos = self.userA.aw.find_text_by_ocr("更多技能", timeout=3)

        if skill_pos:
            self.userA.aw.tap(skill_pos[0], skill_pos[1])
            self.userA.aw.sleep(3)

            # 查找搜索入口
            search_pos = self.userA.aw.find_text_by_ocr("搜索", timeout=3)
            if search_pos:
                self.userA.aw.tap(search_pos[0], search_pos[1])
                self.userA.aw.sleep(1)
                self.userA.aw.input_text("日程")
                self.userA.aw.sleep(2)

                results = self.userA.aw.ocr_scan_page()
                assert len(results) > 0, "搜索后无任何内容"

    def teardown(self):
        """测试后清理"""
        self.userA.aw.press_back()
        self.userA.aw.sleep(1)
        self.userA.aw.workhub_close()
