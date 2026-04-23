"""
测试用例: 搜索入口-综合搜索中有云空间选项
探索来源: AI自主探索POPO App生成
用例描述: 点击搜索框，在搜索指定内容中有一个"云空间"选项
"""
from conftest import BaseTest


class TestSearchCloudOption(BaseTest):
    """搜索入口-综合搜索中云空间选项 测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_search_has_cloud_option(self):
        """
        点击搜索框，验证搜索页面中存在'云空间'选项Tab
        """
        from image.image_name_mapping import MESSAGE_TAB_SEARCH

        # 点击搜索按钮进入搜索页面
        self.userA.click_image(MESSAGE_TAB_SEARCH)

        # 搜索Tab需要左滑才能看到云空间
        # 先找到日程Tab的位置，然后向左滑动
        pos = self.userA.aw.find_text_by_ocr("日程", timeout=5)
        if pos:
            self.userA.aw.swipe_left(pos, 230)

        # 验证云空间Tab存在
        self.userA.text_exists("云空间")

        # 退出搜索页
        from image.image_name_mapping import SEARCH_CANCEL
        self.userA.click_image(SEARCH_CANCEL)

    def teardown(self):
        pass
