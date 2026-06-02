"""
测试用例: 大搜 - 日程搜索 (R18)

R18: CLI造日程 → 搜索页切到日程tab → 搜索日程标题 → 验证结果出现
"""
import subprocess

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchSchedule(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        # CLI 造数：创建一个确定存在的日程，用于搜索验证
        self.schedule_info = self.userA.cli.create_schedule_cli(
            title="搜索功能验证会议",
            start_time="2026-06-10T14:00:00+08:00",
            end_time="2026-06-10T15:00:00+08:00",
        )
        self.schedule_id = self.schedule_info["schedule_id"]

    def test_search_schedule(self):
        """R18: 日程tab搜索已有日程可查到"""
        # 进入搜索页并切到日程tab
        self.userA.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        self.userA.aw.sleep(0.5)
        self.userA.click_text("日程", dy=10)
        self.userA.aw.sleep(0.5)
        # 验证日程搜索页就绪
        assert self.userA.aw.find_text_by_ocr("输入关键词查找日程", timeout=3) is not None, \
            "R18: 日程搜索页未就绪（未找到占位文字）"
        # 输入刚才创建的日程标题关键词
        self.userA.click_image(SELECT_SEARCH, dx=10)
        self.userA.input_text("搜索功能验证")
        self.userA.aw.sleep(1)
        # 验证：能看到我们刚创建的日程标题
        assert self.userA.aw.find_text_by_ocr("搜索功能验证", timeout=8) is not None, \
            "R18: 日程搜索未找到刚创建的日程"
        # 返回消息列表
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        # 清理：取消造数创建的日程
        try:
            subprocess.run(
                ["popo-cli", "popo", "calendar_schedule_cancel",
                 f"scheduleId={self.schedule_id}"],
                shell=True, capture_output=True, text=True, encoding="utf-8",
            )
        except Exception:
            pass
