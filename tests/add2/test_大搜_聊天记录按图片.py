"""
测试用例: 大搜 - 聊天记录按图片视频查看 (R32)

R32: CLI造群+发图片 → 进入群聊 → 群设置 → "图片/视频"面板 → 验证月份分组
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestChatHistoryByImage(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        # CLI 造数：创建测试群并发送一张图片
        self.tid, self.gname = self.userA.cli.create_team_cli(
            uid_list=["grp.popoqa50@corp.netease.com"],
            name="图片记录测试群",
        )
        self.userA.cli.send_message_team_cli(
            tid=self.tid,
            image_path="E:/UIAutotest/image/登录页-网易popo文案.png",
        )
        # 造数完成后 App 仍在消息列表页

    def test_chat_history_by_image(self):
        """R32: 聊天记录按图片/视频查看"""
        # 通过 send_message 进入群聊，isback=False 留在聊天页
        self.userA.aw.send_message(recipient=self.tid, message="进群", isback=False)
        # 点击群名称/群成员区域进入群设置
        self.userA.click_image(MSG_team_CALL, region=Normal.HALF_UP, dx=-150)
        time.sleep(0.5)
        # 进入群设置后找到"图片/视频"标签
        self.userA.aw.click_text("图片/视频", region=Normal.HALF_DOWN)
        time.sleep(0.5)
        # 验证有图片月份分组出现
        self.userA.text_exists("本月", timeout=5)
        # 返回消息列表
        self.userA.return_to_message_list()

    def teardown(self):
        # 测试群为临时数据，无需清理
        pass
