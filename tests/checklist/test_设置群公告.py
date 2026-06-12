"""
测试用例: 设置群公告
探索补全: 原始用例步骤模糊，通过自主探索App补全操作路径
探索来源: explorer_output/knowledge/app_map.json features.set_announcement
"""
from conftest import BaseTest


class TestSetGroupAnnouncement(BaseTest):
    """设置群公告功能测试"""

    def setup(self):
        self.userA = self.users("userA")
        self.group_name = self.userA.setup_owner_group("自动化测试群主群")

    def test_set_group_announcement(self):
        """
        测试设置群公告

        步骤:
        1. 搜索群聊并进入群设置
        2. 点击"群公告"进入群公告查看页
        3. 点击"编辑"进入编辑模式
        4. 清空旧内容，输入新公告
        5. 点击右上角完成按钮
        6. 处理"发送到群聊"确认弹窗
        7. 返回消息列表页
        """
        self.userA.set_group_announcement(
            group_identifier=self.group_name,
            content="自动化测试群公告内容"
        )

    def teardown(self):
        pass
