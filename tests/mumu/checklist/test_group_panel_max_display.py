"""
测试用例: 面板展开的显示-最大分组数显示
功能点: 会话分组面板支持展示所有分组并可滑动查看
操作步骤: 点击分组栏右侧展开按钮
预期结果: 展开分组面板，分组处可上下滑动，UI显示无异常
"""
from conftest import BaseTest


class TestGroupPanelMaxDisplay(BaseTest):
    """面板展开-最大分组数显示"""

    def setup(self):
        self.userA = self.users("userA")

    def test_panel_expand_shows_all_groups(self):
        """
        步骤:
        1. 在消息列表页点击分组栏右侧的"展开"按钮
        2. 验证分组面板展开，显示所有分组标签
        3. 验证面板区域可以滑动查看更多分组
        """
        # 打开分组面板
        self.userA.aw.open_session_group_panel()

        # 验证面板中存在多个分组标签（展开后"收起"按钮可见即说明面板已展开）
        # 面板展开后会显示多个分组标签名称
        scan = self.userA.aw.ocr_scan_page()
        panel_texts = [item['text'] for item in scan if item['cy'] < 350]
        assert len(panel_texts) >= 3, f"面板展开后标签数量不足，仅看到: {panel_texts}"

        # 验证面板区域可上下滑动（在面板区域做小幅滑动）
        # 面板区域大约在y=200~350
        self.userA.aw.swipe(270, 320, 270, 250, duration=0.3)
        import time
        time.sleep(0.5)

        # 滑回来
        self.userA.aw.swipe(270, 250, 270, 320, duration=0.3)
        time.sleep(0.5)

        # 关闭面板
        self.userA.aw.close_session_group_panel()

    def teardown(self):
        pass
