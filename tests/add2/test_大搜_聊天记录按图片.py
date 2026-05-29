"""
测试用例: 大搜 - 聊天记录按图片视频查看 (R32/R33)

R32: 进入群设置 → 点"图片/视频"面板 → 验证月份分组出现
R33: 点击第一张缩略图 → 进入预览/播放器
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestChatHistoryByImage(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_chat_history_by_image(self):
        """R32/R33: 聊天记录按图片/视频查看 + 点击缩略图预览"""
        # 搜索群聊并进入
        self.userA.search(tab="群", text="吴彦祖", isclose=False)
        time.sleep(0.5)
        # 点击第一个群结果进入聊天页
        self.userA.click_text("吴彦祖", region=Search.RESULT_LIST)
        time.sleep(0.5)
        # 点击群名称区域进入群设置
        self.userA.click_text("名群成员", region=Normal.HALF_UP)
        # 点击"图片/视频"标签 (R32)
        self.userA.click_text("图片/视频", region=Normal.HALF_DOWN, dy=-20)
        time.sleep(0.5)

        self.userA.click_text("本月", dy=110)
        # 验证进入预览/播放器
        self.userA.aw.long_press(350, 450, duration=2)
        self.userA.text_exists("提取文字")

    def teardown(self):
        pass
