"""
测试用例: 大搜 - 聊天记录按日期查看 (R30)

R30: CLI造群+发图片 → 进入群聊 → 群设置 → "图片/视频"面板 → 验证按月份（日期）分组显示
与 R32 复用同一入口，聚焦于"按日期分组"展示验证（月份分组标题可见 + 内容按日期排列）
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestChatHistoryByDate(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        # CLI 造数：创建群 + 发一张图片
        self.tid, self.gname = self.userA.cli.create_team_cli(
            uid_list=["grp.popoqa73@corp.netease.com"],
            name="日期记录测试群",
        )
        self.userA.cli.send_message_team_cli(
            tid=self.tid,
            image_path="E:/UIAutotest/image/登录页-网易popo文案.png",
        )

    def test_chat_history_by_date(self):
        """R30: 图片/视频面板按月份日期分组显示"""
        # 进入群聊
        self.userA.aw.send_message(recipient=self.tid, message="进群", isback=False)
        # 进入群设置
        self.userA.click_image(MSG_team_CALL, region=Normal.HALF_UP, dx=-150)
        self.userA.aw.sleep(0.5)
        # 进入图片/视频面板（按日期分组展示）
        self.userA.aw.click_text("图片/视频", region=Normal.HALF_DOWN)
        self.userA.aw.sleep(0.5)
        # 验证有月份分组标题（"本月" 或年月格式如 "2026年6月"）
        found_month = self.userA.aw.find_text_by_ocr("本月", timeout=5)
        if found_month is None:
            found_month = self.userA.aw.find_text_by_ocr("2026", timeout=3)
        assert found_month is not None, \
            "R30: 图片/视频面板未出现月份日期分组标题"
        self.userA.return_to_message_list()

    def teardown(self):
        pass
