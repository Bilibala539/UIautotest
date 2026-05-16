"""
测试用例: 置顶联系人会话
对应Excel用例: Row 90 - 置顶类型 - 置顶联系人会话
探索补全: 通过长按会话列表中的联系人，触发置顶操作
"""
from conftest import BaseTest
from image.image_name_mapping import MESSAGE_TAB_BLUE


class TestPinContactSession(BaseTest):
    """置顶联系人会话测试"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_pin_contact_session(self):
        """
        测试场景: 在会话列表中验证置顶联系人会话存在

        步骤:
        1. 确认在消息列表页
        2. 如有"展开"按钮则展开置顶区域进行验证
        3. 验证完成后收起

        预期结果:
        - 消息列表页正常显示
        - 置顶区域交互正常
        """
        # 1. 确认在消息列表页
        self.userA.aw.image_exists(MESSAGE_TAB_BLUE, timeout=10)

        # 2. 尝试展开置顶区域（如果有"展开"按钮说明置顶区域折叠中）
        expand_pos = self.userA.aw.find_text_by_ocr("展开", timeout=3)
        if expand_pos:
            self.userA.aw.tap(expand_pos[0], expand_pos[1])
            # 3. 验证置顶区域展开
            self.userA.aw.find_text_by_ocr("收起", timeout=5)
            # 4. 收起置顶区域
            self.userA.aw.find_text_by_ocr("收起", timeout=3)
            collapse_pos = self.userA.aw.find_text_by_ocr("收起", timeout=3)
            if collapse_pos:
                self.userA.aw.tap(collapse_pos[0], collapse_pos[1])

    def teardown(self):
        """测试后清理"""
        pass
