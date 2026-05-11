"""
测试用例: WorkHub入口验证
验证从POPO搜索页"问AI"Tab可以正确进入WorkHub首页
"""
from conftest import BaseTest


class TestWorkhubEntrance(BaseTest):
    """WorkHub入口验证"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_enter_workhub_from_search(self):
        """
        验证从搜索页"问AI"Tab进入WorkHub
        
        步骤:
        1. 在消息列表页点击搜索按钮
        2. 点击"问AI"Tab
        3. 验证WorkHub首页加载完成（显示WorkHub标题）
        
        预期结果:
        - 页面显示"WorkHub"标题
        - 页面显示输入框（"分配任务或提问"）
        """
        # 进入WorkHub
        self.userA.aw.enter_workhub()

        # 验证WorkHub标题存在
        self.userA.aw.text_exists("WorkHub", timeout=5)

        # 验证输入框存在
        self.userA.aw.text_exists("分配任务或提问", timeout=5)

    def teardown(self):
        """测试后清理 - 退出WorkHub"""
        self.userA.aw.workhub_close()
