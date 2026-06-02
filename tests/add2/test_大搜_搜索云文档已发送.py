"""
测试用例: 大搜 - 搜索云文档（已发送过）(R14)

R14: 云空间创建的文档（在会话区发送过）
- 全部/云空间页签和消息页签都能搜索到
"""
import json
import subprocess
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchCloudDocSent(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        self.doc_id = None
        self.doc_title = f"autotest_R14_已发送文档"

        # CLI造数: 创建云文档
        result = subprocess.run(
            ["popo-cli", "popo", "doc_create_doc",
             "docType=2", f"title={self.doc_title}"],
            capture_output=True, text=True, encoding="utf-8", shell=True
        )
        data = json.loads(result.stdout)
        inner = data["data"]["data"]["data"]
        self.doc_id = inner["docId"]
        self.doc_url = inner["url"]

        # 将文档链接发送到会话中
        subprocess.run(
            ["popo-cli", "popo", "message_send_p2p",
             f"message={self.doc_url}",
             "receiver=grp.popoqa50@corp.netease.com", "source=AGENT"],
            capture_output=True, text=True, encoding="utf-8", shell=True
        )
        time.sleep(5)  # 等待消息索引和云文档索引生效

    def test_cloud_doc_sent_search_in_cloud_tab(self):
        """R14: 已发送的云文档在云空间tab能搜到"""
        self.userA.search(tab="云空间", text=self.doc_title, isclose=False)
        self.userA.aw.sleep(3)
        # 验证: 云空间tab能搜到
        found = self.userA.aw.find_text_by_ocr(self.doc_title, timeout=8, region=Search.RESULT_LIST)
        assert found is not None, f"云空间tab应能搜到已发送的云文档'{self.doc_title}'"
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def test_cloud_doc_sent_search_in_message_tab(self):
        """R14: 已发送的云文档在消息tab也能搜到"""
        self.userA.search(tab="消息", text=self.doc_title, isclose=False)
        self.userA.aw.sleep(3)
        # 验证: 消息tab能搜到（因为文档链接已通过消息发送）
        found = self.userA.aw.find_text_by_ocr(self.doc_title, timeout=8, region=Search.RESULT_LIST)
        assert found is not None, f"消息tab应能搜到已发送的云文档'{self.doc_title}'"
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        # 清理: 删除测试用云文档
        if self.doc_id:
            subprocess.run(
                ["popo-cli", "popo", "doc_delete_doc", f"docId={self.doc_id}"],
                capture_output=True, text=True, encoding="utf-8", shell=True
            )
