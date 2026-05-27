"""
测试用例: 图片复制到输入框
探索来源: AI自主探索POPO App生成
探索补全: 长按图片→复制→粘贴到输入框→发送
"""
from conftest import BaseTest


class TestCopyImageToInput(BaseTest):
    """图片复制到输入框功能测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_copy_image_to_input_and_send(self):
        """
        测试图片复制到输入框功能

        步骤:
        1. 进入 grp.popoqa50 聊天页面
        2. 从相册发送一张图片
        3. 长按已发送的图片，点击"复制"
        4. 验证"复制成功"提示
        5. 点击输入框 → 长按输入框 → 点击"粘贴"
        6. 点击发送
        7. 验证发送成功（+号恢复）
        8. 返回消息列表
        """
        self.userA.copy_image_to_input_and_send(recipient="grp.popoqa50")

    def teardown(self):
        pass
