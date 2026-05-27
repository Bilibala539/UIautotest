"""
测试用例: 长按会话预览
探索来源: AI自主探索POPO App
用例描述: 在消息列表页长按会话项，验证弹出操作菜单
"""
import time
from conftest import BaseTest
from image.image_name_mapping import MESSAGE_TAB_BLUE, SESSIONLIST_PLUS_BUTTON


class TestLongPressSessionPreview(BaseTest):
    """长按会话预览 测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_long_press_session_preview(self):
        """
        步骤:
        1. 确认在消息列表页
        2. 以右上角+按钮为锚点，对下方第一个会话项区域进行长按
        3. 验证弹出操作菜单（至少含一个已知选项）
        4. 按返回键关闭菜单
        """
        # 确认在消息列表页
        self.userA.aw.image_exists(MESSAGE_TAB_BLUE, timeout=10)

        # 以右上角+按钮为锚点，长按其下方左侧的会话区域
        plus_pos = self.userA.aw.find_image(SESSIONLIST_PLUS_BUTTON, timeout=5)
        assert plus_pos is not None, "未找到消息列表右上角+按钮"
        lx, ly = plus_pos[0] - 240, plus_pos[1] + 50
        self.userA.aw.long_press(lx, ly, duration=1.5)
        time.sleep(1)

        # 验证弹出了长按操作菜单：逐一检测常见菜单项
        menu_items = ["置顶", "取消置顶", "设为未读", "标记已读",
                       "管理分组", "添加到分组", "删除会话", "待处理"]
        found = None
        for item in menu_items:
            found = self.userA.aw.find_text_by_ocr(item, timeout=2)
            if found:
                break
        assert found is not None, f"未弹出长按操作菜单，已检测: {menu_items}"

        # 按返回键关闭菜单
        self.userA.aw.press_back()
        time.sleep(0.5)

    def teardown(self):
        pass
