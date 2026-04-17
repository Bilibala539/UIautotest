"""
测试用例: 长按图片消息后编辑
探索来源: AI自主探索POPO App生成

测试步骤:
1. 进入联系人聊天页并发送一张图片（前置条件）
2. 长按已发送的图片消息气泡
3. 点击弹出菜单中的"编辑图片"
4. 验证进入图片编辑器（底部工具栏出现）
5. 点击"完成"完成编辑
6. 验证回到聊天页
"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa93"


class TestEditImageFromChatMessage(BaseTest):
    """长按图片消息进行编辑测试"""

    def setup(self):
        self.userA = self.users("userA")
        self.userA.login()

    def test_edit_image_from_chat_message(self):
        """
        长按聊天中的图片消息 → 点击编辑图片 → 完成

        前置条件: 先从相册发送一张图片到聊天，保持在聊天页面
        """
        # 先发一张图片（不返回，留在聊天页面）
        self.userA.send_image_from_album(RECIPIENT)

        # 长按图片消息，进入编辑器，完成
        result = self.userA.edit_image_from_chat_message(RECIPIENT)
        assert result, "长按图片消息并编辑应该成功"

    def teardown(self):
        try:
            self.userA.logout()
        finally:
            self.userA.aw.stop_app()
