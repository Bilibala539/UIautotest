"""
测试用例: 从相册选图编辑后发送
探索来源: AI自主探索POPO App生成

测试步骤:
1. 进入联系人聊天页
2. 点击 + → 相册
3. 选择第一张图片 → 点击预览
4. 点击"编辑"进入图片编辑器
5. 验证编辑器底部工具栏显示
6. 点击"完成"退出编辑器
7. 点击"发送"发送图片
8. 验证发送成功（回到聊天页）
"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa93"


class TestSelectEditSendImageFromAlbum(BaseTest):
    """从相册选图编辑后发送测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_select_edit_send_image_from_album(self):
        """
        从相册选图 → 预览 → 编辑 → 完成 → 发送
        """
        result = self.userA.select_edit_send_image_from_album(RECIPIENT)
        assert result, "从相册选图编辑后发送应该成功"

    def teardown(self):
        pass
