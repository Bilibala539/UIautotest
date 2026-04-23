"""
测试用例: 合并消息图片滑动
探索来源: AI自主探索POPO App生成
探索补全: 发送多张图片→合并转发→进入合并消息详情→图片查看器左右滑动
"""
from conftest import BaseTest


class TestMergeForwardImagesSwipe(BaseTest):
    """合并消息图片滑动功能测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_merge_forward_images_and_swipe(self):
        """
        测试合并消息图片查看器中的滑动浏览功能

        步骤:
        1. 进入 grp.popoqa50 聊天页面
        2. 从相册选3张图片同时发送
        3. 长按图片→多选→选中多张→合并转发
        4. 转发到 grp.popoqa50
        5. 点击合并消息卡片"聊天记录"进入详情页
        6. 点击详情页中图片进入全屏查看器
        7. 左滑、右滑浏览图片
        8. 返回消息列表
        """
        self.userA.merge_forward_images_and_swipe(recipient="grp.popoqa50")

    def teardown(self):
        pass
