"""
测试用例: 大搜 - 聊天记录按链接查看 (R33)

R33: CLI造群+发含URL的消息 → 进入群聊 → 群设置 → "链接"面板 → 验证链接出现
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestChatHistoryByLink(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        # CLI 造数：创建群 + 发一条含 URL 的消息
        self.tid, self.gname = self.userA.cli.create_team_cli(
            uid_list=["grp.popoqa73@corp.netease.com"],
            name="链接记录测试群",
        )
        self.userA.cli.send_message_team_cli(
            tid=self.tid,
            message="自动化测试链接 https://www.netease.com",
        )

    def test_chat_history_by_link(self):
        """R33: 聊天记录链接面板中能看到刚发送的链接"""
        # 进入群聊
        self.userA.aw.send_message(recipient=self.tid, message="进群", isback=False)
        # 点击群成员/群名称区域进入群设置
        self.userA.click_image(MSG_team_CALL, region=Normal.HALF_UP, dx=-150)
        self.userA.aw.sleep(0.5)
        # 切到链接标签
        self.userA.aw.click_text("链接", region=Normal.HALF_DOWN)
        self.userA.aw.sleep(0.5)
        # 验证链接内容出现（netease.com 或"自动化测试链接"）
        found = self.userA.aw.find_text_by_ocr("netease", timeout=5)
        if found is None:
            found = self.userA.aw.find_text_by_ocr("自动化测试链接", timeout=3)
        assert found is not None, "R33: 链接面板未找到发送的链接消息"
        self.userA.return_to_message_list()

    def teardown(self):
        pass
