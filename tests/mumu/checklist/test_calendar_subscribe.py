"""
测试用例: 订阅日历本（Excel 日历模块.xlsx Sheet2 行 R36）

Excel 原始步骤:
  1. 点击【我的订阅】右侧的加号
  2. 输入任意日历本名字
  3. 点击订阅

Excel 预期结果:
  1. 提示已订阅，原本的订阅按钮变为退订
  2. 日历本显示在侧边栏【我的订阅】一栏下

实现说明:
  新版 POPO "任务管理"UI 中"我的订阅"对应"我关注的"区域；订阅交互内层
  （搜索框 / 订阅按钮 / 退订按钮）的元素图尚未截图，待 explorer/element
  补图后才能写完整流程。
  本文件先交付一条到"我关注的列表页"为止的入口验证用例，作为后续完整
  订阅流程的导航前置；剩余步骤通过 skip 显式占位避免被遗忘。
"""
import pytest

from conftest import BaseTest


class TestCalendarSubscribe(BaseTest):
    """订阅日历本测试类（R36）"""

    def setup(self):
        self.userA = self.users("userA")

    def test_open_my_followed_calendar_entry(self):
        """
        验证 R36 订阅入口可达

        步骤:
        1. 从消息列表导航至任务管理页（新版日历本管理入口）
        2. 点击"我关注的"进入订阅区域
        3. 断言已离开任务管理首页（CAL_BOOK_MY_CREATED 不再可见）

        本用例只覆盖 R36 步骤 0（前置导航），不点击加号、不输入、不订阅。
        待 element 补全订阅面板元素后再扩展到完整 R36。
        """
        result = self.userA.open_my_followed_calendar_book_list()
        assert result, "应当能成功进入'我关注的'列表页"

    @pytest.mark.skip(
        reason="R36 完整流程: 需要新版 UI 的'我关注的'页内'+ → 搜索日历本 → "
               "订阅按钮 → 退订按钮 → 列表回归验证'共 5 类元素图，"
               "目前 image_ai 仅有任务管理首页 4 张图，需 explorer 探索新版"
               "订阅路径并 element 截图后启用"
    )
    def test_subscribe_calendar_book_full(self):
        """
        R36 完整流程: 进入'我关注的'页 → +号 → 输入名字 → 点订阅
        → 验证按钮变退订 → 列表出现该日历本

        当前被 skip，元素补齐后启用。
        """
        raise NotImplementedError("待元素补齐后实现")

    def teardown(self):
        pass
