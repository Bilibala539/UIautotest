"""
测试用例: 大搜 - 搜索云文档（未发送过）(R13)

R13: 云空间创建的文档（没有在会话区发送过）
- 在全部/云空间页签搜索云文档名称 -> 能搜索到
- 在消息页签搜索云文档名称 -> 无法搜索到
"""
import json
import subprocess
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchCloudDocUnsent(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        self.doc_id = None
        self.doc_title = f"autotest_R13_未发送文档"

        # CLI造数: 创建云文档（不发送到会话）
        result = subprocess.run(
            ["popo-cli", "popo", "doc_create_doc",
             "docType=2", f"title={self.doc_title}"],
            capture_output=True, text=True, encoding="utf-8", shell=True
        )
        data = json.loads(result.stdout)
        self.doc_id = data["data"]["data"]["data"]["docId"]
        time.sleep(3)  # 等待索引生效

    def test_cloud_doc_unsent_search_in_cloud_tab(self):
        """R13: 未发送的云文档在云空间tab能搜到"""
        self.userA.search(tab="云空间", text=self.doc_title, isclose=False)
        self.userA.aw.sleep(3)
        # 验证: 云空间tab能搜到该文档
        found = self.userA.aw.find_text_by_ocr(self.doc_title, timeout=8, region=Search.RESULT_LIST)
        assert found is not None, f"云空间tab应能搜到未发送的云文档'{self.doc_title}'"
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def test_cloud_doc_unsent_not_in_message_tab(self):
        """R13: 未发送的云文档在消息tab搜不到"""
        self.userA.search(tab="消息", text=self.doc_title, isclose=False)
        self.userA.aw.sleep(3)
        # 验证: 消息tab搜不到该文档
        self.userA.text_not_exists(self.doc_title, region=Search.RESULT_LIST, timeout=5)
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        # 清理: 删除测试用云文档
        if self.doc_id:
            subprocess.run(
                ["popo-cli", "popo", "doc_delete_doc", f"docId={self.doc_id}"],
                capture_output=True, text=True, encoding="utf-8", shell=True
            )
