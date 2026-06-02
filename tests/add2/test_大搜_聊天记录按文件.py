"""
测试用例: 大搜 - 聊天记录按文件查看 (R31)

R31: CLI造群+发文件 → 进入群聊 → 群设置 → "文件"面板 → 验证文件出现
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestChatHistoryByFile(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        # CLI 造数：创建群 + 发一个文件
        self.tid, self.gname = self.userA.cli.create_team_cli(
            uid_list=["grp.popoqa73@corp.netease.com"],
            name="文件记录测试群",
        )
        self.fname, _ = self.userA.cli.send_message_team_cli(
            tid=self.tid,
            file_path="E:/UIAutotest/pytest.ini",
        )

    def test_chat_history_by_file(self):
        """R31: 聊天记录文件面板中能看到刚发送的文件"""
        # 进入群聊
        self.userA.aw.send_message(recipient=self.tid, message="进群", isback=False)
        # 点击群成员/群名称区域进入群设置
        self.userA.click_image(MSG_team_CALL, region=Normal.HALF_UP, dx=-150)
        self.userA.aw.sleep(0.5)
        # 切到文件标签
        self.userA.aw.click_text("文件", region=Normal.HALF_DOWN)
        self.userA.aw.sleep(0.5)
        # 验证文件名出现在列表中（pytest.ini 关键词 "pytest"）
        assert self.userA.aw.find_text_by_ocr("pytest", timeout=5) is not None, \
            "R31: 文件面板未找到发送的文件"
        self.userA.return_to_message_list()

    def teardown(self):
        pass
