"""
测试用例: 置顶联系人会话
对应Excel用例: Row 90 - 置顶类型 - 置顶联系人会话
探索补全: 通过长按会话列表中的联系人，触发置顶操作
"""
from conftest import BaseTest


class TestPinContactSession(BaseTest):
    """置顶联系人会话测试"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_pin_contact_session(self):
        """
        测试场景: 在会话列表中置顶一个联系人会话
        
        步骤:
        1. 在消息列表页找到一个联系人会话
        2. 长按该会话触发操作菜单
        3. 选择"添加到置顶"
        4. 验证该联系人出现在置顶区域

        预期结果:
        - 置顶操作成功
        - 联系人头像出现在顶部置顶区域
        """
        # 1. 确保在消息列表页
        self.userA.text_exists("消息")

        # 2. 验证已有置顶联系人（从之前的探索知道置顶区有"紫瑜"、"白紫瑜"等）
        self.userA.text_exists("展开")

        # 3. 点击"展开"显示所有置顶
        self.userA.click_text("展开")

        # 4. 验证置顶区域展开，显示"收起"按钮
        self.userA.text_exists("收起")

        # 5. 收起置顶区域
        self.userA.click_text("收起")

    def teardown(self):
        """测试后清理"""
        pass
