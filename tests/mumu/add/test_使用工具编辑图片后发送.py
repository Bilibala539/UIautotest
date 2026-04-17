"""
测试用例: 使用编辑工具编辑图片后发送
探索来源: AI自主探索POPO App生成

测试步骤:
1. 进入联系人聊天页
2. 点击 + → 相册 → 选图 → 预览 → 编辑
3. 在图片编辑器中使用画笔工具绘制
4. 点击"完成"退出编辑器
5. 点击"发送"发送编辑后的图片
6. 验证发送成功（回到聊天页）
"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa93"


class TestEditWithToolsSendImage(BaseTest):
    """使用编辑工具编辑图片后发送测试"""

    def setup(self):
        self.userA = self.users("userA")
        self.userA.login()

    def test_edit_with_tools_send_image(self):
        """
        从相册选图 → 进入编辑器 → 使用画笔工具编辑 → 完成 → 发送
        """
        result = self.userA.select_edit_with_tools_send_image(RECIPIENT)
        assert result, "使用工具编辑图片后发送应该成功"

    def teardown(self):
        try:
            self.userA.logout()
        finally:
            self.userA.aw.stop_app()
