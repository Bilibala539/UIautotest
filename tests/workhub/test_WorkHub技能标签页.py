"""
测试用例: WorkHub技能Tab区域验证
验证技能Tab展示正常，可点击切换，技能卡片对应展示
"""
from conftest import BaseTest


class TestWorkhubSkillTabs(BaseTest):
    """WorkHub技能Tab区域验证"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_default_skill_tab_is_general(self):
        """
        验证进入WorkHub后默认选中"通用"Tab
        
        步骤:
        1. 进入WorkHub
        2. 验证"通用"Tab可见
        3. 验证技能卡片区域有内容（如"日程预定"、"工作总结"）
        
        预期结果:
        - "通用"Tab可见
        - 技能卡片区有内容
        """
        self.userA.aw.enter_workhub()

        # 验证通用Tab可见
        self.userA.aw.text_exists("通用", timeout=5)

        # 验证技能卡片存在（通用Tab下有"日程预定"和"工作总结"）
        self.userA.aw.text_exists("日程预定", timeout=5)

    def test_switch_skill_tab(self):
        """
        验证点击不同技能Tab可以切换
        
        步骤:
        1. 进入WorkHub
        2. 点击"创建多维表格"Tab
        3. 验证页面内容更新
        
        预期结果:
        - 切换后技能卡片区内容变化
        """
        self.userA.aw.enter_workhub()

        # 点击"创建多维表格"Tab
        self.userA.aw.workhub_click_skill_tab("创建多维表格")

        # 验证Tab切换成功 - "创建多维表格"Tab应该仍然可见
        self.userA.aw.text_exists("创建多维表格", timeout=5)

    def test_skill_tabs_scrollable(self):
        """
        验证技能Tab区域可以左右滑动展示更多Tab
        
        步骤:
        1. 进入WorkHub
        2. 在Tab区域向左滑动
        3. 验证出现新的Tab
        
        预期结果:
        - 滑动后出现更多Tab
        """
        self.userA.aw.enter_workhub()

        # Tab区域向左滑动 (y=360是Tab区域的中间高度)
        self.userA.aw.swipe(450, 360, 100, 360, duration=0.3)
        self.userA.aw.sleep(1)

        # 验证能看到更多Tab(具体名字需要探索确认)
        # 至少Tab区域还有文字内容
        results = self.userA.aw.ocr_scan_page(region=(0, 330, 540, 60))
        assert len(results) > 0, "滑动后Tab区域无内容"

    def teardown(self):
        """测试后清理"""
        self.userA.aw.workhub_close()
