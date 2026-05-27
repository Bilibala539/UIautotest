"""
测试用例: WorkHub侧边栏验证
验证左上角汉堡按钮可打开侧边栏，侧边栏中显示订阅、历史记录等内容
"""
from conftest import BaseTest


class TestWorkhubSidebar(BaseTest):
    """WorkHub侧边栏验证"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_open_sidebar(self):
        """
        验证点击左上角汉堡按钮可打开侧边栏
        
        步骤:
        1. 进入WorkHub
        2. 点击左上角汉堡按钮
        3. 验证侧边栏出现
        
        预期结果:
        - 侧边栏打开，可见"订阅"或"历史记录"
        """
        self.userA.aw.enter_workhub()

        # 打开侧边栏
        result = self.userA.aw.workhub_open_sidebar()
        assert result, "侧边栏未能打开"

    def test_sidebar_has_new_dialog(self):
        """
        验证侧边栏中有"+新对话"按钮
        
        步骤:
        1. 进入WorkHub
        2. 打开侧边栏
        3. 验证"+新对话"按钮可见
        
        预期结果:
        - 侧边栏中显示"新对话"
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()

        # 验证"新对话"按钮
        self.userA.aw.text_exists("新对话", timeout=5)

    def test_sidebar_new_dialog(self):
        """
        验证点击"+新对话"可以创建新对话
        
        步骤:
        1. 进入WorkHub
        2. 打开侧边栏
        3. 点击"+新对话"
        4. 验证新对话页面出现（显示输入框或欢迎文案）
        
        预期结果:
        - 新对话创建成功，侧边栏关闭，进入新对话页面
        
        探索补全: 点击新对话后进入新对话界面，可能显示欢迎文案或输入框
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()

        # 点击新对话
        self.userA.aw.workhub_sidebar_new_dialog()
        self.userA.aw.sleep(3)

        # 验证进入了新对话页面 - 侧边栏应已关闭，显示输入框或WorkHub标题
        # 新对话页面应该有输入框
        input_pos = self.userA.aw.find_text_by_ocr("分配任务或提问", timeout=5)
        workhub_pos = self.userA.aw.find_text_by_ocr("WorkHub", timeout=3)
        assert input_pos or workhub_pos, "新对话页面未正确显示"

    def teardown(self):
        """测试后清理"""
        self.userA.aw.workhub_close()
