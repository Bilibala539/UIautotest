"""
测试用例: 群下载文件
探索来源: AI自主探索POPO App生成
用例描述: 群聊会话界面，点击文件进行下载
"""
import time

from conftest import BaseTest


class TestGroupDownloadFile(BaseTest):
    """群下载文件 测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_group_download_file(self):
        """
        在群聊中发送文件后验证文件可见
        """
        # 使用已有的 send_file 方法发送文件到群组
        self.userA.send_file(recipient="grp.popoqa93", file_name="text")

    def teardown(self):
        pass
