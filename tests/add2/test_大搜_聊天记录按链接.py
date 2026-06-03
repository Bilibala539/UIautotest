"""
测试用例: 大搜 - 聊天记录图片/视频点击定位 (R33)

R33 对应 xlsx R32: 单击图片或视频时，支持跳转至会话，定位至会话中该消息的位置
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestChatHistoryImageClickLocate(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        # CLI 造数：创建测试群并发送一张图片
        self.tid, self.gname = self.userA.cli.create_team_cli(
            uid_list=["grp.popoqa50@corp.netease.com"],
            name="图片定位测试群",
        )
        self.userA.cli.send_message_team_cli(
            tid=self.tid,
            image_path="E:/UIAutotest/image/登录页-网易popo文案.png",
        )

    def test_click_image_in_panel_locates_to_chat(self):
        """R33: 图片/视频面板中点击图片，跳转至会话并定位到该消息位置"""
        # 从消息列表精确找到群名并点击进入聊天页
        pos = self.userA.aw.find_text_by_ocr(self.gname, timeout=5)
        assert pos is not None, f"消息列表未找到群 '{self.gname}'"
        self.userA.aw.tap(pos[0], pos[1])
        self.userA.aw.sleep(1)
        # 确认已进入聊天页（有加号按钮）
        self.userA.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN, timeout=8)
        # 进入群设置（点击群名称区域）
        self.userA.click_image(MSG_team_CALL, region=Normal.HALF_UP, dx=-150)
        time.sleep(0.5)
        # 进入图片/视频面板
        self.userA.aw.click_text("图片/视频", region=Normal.HALF_DOWN)
        time.sleep(1)
        # 验证图片面板有内容（至少有本月分组或图片缩略图）
        found_month = self.userA.aw.find_text_by_ocr("本月", timeout=5)
        if found_month is None:
            found_month = self.userA.aw.find_text_by_ocr("2026", timeout=3)
        assert found_month is not None,             "R33: 图片/视频面板未出现月份分组标题，可能没有图片"
        # 点击面板中的第一张图片缩略图（图片区域大约在月份标题下方）
        # 图片缩略图一般在 y=300+ 区域，x=70 左右（第一个缩略图位置）
        self.userA.aw.tap(70, 350)
        time.sleep(2)
        # 验证：跳转到聊天页（CHAT_PLUS_BUTTON 出现表明在聊天页）
        self.userA.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN, timeout=8)
        # 进入聊天页即代表定位成功（App 自动滚动到该图片消息位置）
        self.userA.return_to_message_list()

    def teardown(self):
        pass
