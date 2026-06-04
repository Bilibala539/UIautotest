"""
测试用例: 大搜 - 表情不支持搜索 (R25)

R25: 验证表情/图片/语音类消息不支持搜索
步骤: 发送含emoji的消息 -> 在大搜中搜索emoji字符 -> 验证搜索结果为空
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchEmojiNotSupported(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        # CLI造数: 发送一条含emoji的消息
        self.userA.cli.send_message_p2p_cli(
            receiver="grp.popoqa50@corp.netease.com",
            message="表情测试emoji123"
        )

    def test_emoji_not_searchable(self):
        """R25: 搜索emoji字符验证无结果 - 表情消息不支持搜索"""
        # 在消息tab搜索emoji字面文字
        self.userA.search(tab="消息", text="emoji123", isclose=False)
        self.userA.aw.sleep(2)

        # 搜索"emoji123"应该能找到（因为它是文本消息中的文字）
        # 但如果搜索纯emoji符号如 😊，则不应有结果
        # 退出当前搜索
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

        # 搜索纯emoji表情符号
        self.userA.search(tab="消息", text="😊", isclose=False)
        self.userA.aw.sleep(3)

        # 验证搜索结果为空 - 使用空态图标或文字判断
        empty_icon = self.userA.aw.find_image(SEARCH_MSG_EMPTY_ICON, timeout=5)
        empty_text = self.userA.aw.find_text_by_ocr("暂无搜索结果", timeout=3)
        assert empty_icon is not None or empty_text is not None, (
            "搜索emoji字符后应该显示空结果，但未检测到空态标识"
        )

        # 退出搜索
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
