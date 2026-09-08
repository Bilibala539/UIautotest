"""OtpClient 单元测试：基于本地网关服务验证轮询、超时与消费。"""
import tempfile
import threading
import unittest
from pathlib import Path

from scripts.otp_gateway.server import create_server
from utils.otp_client import OtpClient, OtpClientError


class OtpClientTest(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.server = create_server(
            "127.0.0.1",
            0,
            Path(self.temp_directory.name) / "otp.sqlite3",
            "ingest-secret",
            "read-secret",
            allowed_phones={"13777777777"},
            ingest_auth_required=True,
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.client = OtpClient(
            base_url=f"http://127.0.0.1:{self.server.server_address[1]}",
            request_timeout=2.0,
        )

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp_directory.cleanup()

    def _push(self, phone: str, code: str) -> None:
        import json
        import urllib.request

        request = urllib.request.Request(
            self.client.base_url + "/api/test/otp",
            data=json.dumps({"phone": phone, "code": code}).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": "Bearer ingest-secret",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(request) as response:
            self.assertEqual(response.status, 201)

    def test_get_code_returns_latest_record(self):
        self._push("13777777777", "123456")
        self._push("13777777777", "654321")

        record = self.client.get_code("13777777777", wait=5, interval=0.2)

        self.assertEqual(record["code"], "654321")
        self.assertEqual(record["phone"], "13777777777")

    def test_get_code_polls_until_available(self):
        def push_later():
            threading.Event().wait(1.0)
            self._push("13777777777", "246810")

        thread = threading.Thread(target=push_later, daemon=True)
        thread.start()

        record = self.client.get_code("13777777777", wait=10, interval=0.2)

        self.assertEqual(record["code"], "246810")

    def test_get_code_timeout(self):
        with self.assertRaises(OtpClientError):
            self.client.get_code("13777777777", wait=1.0, interval=0.2)

    def test_consume_makes_code_unavailable(self):
        self._push("13777777777", "135790")
        record = self.client.get_code("13777777777", wait=5, interval=0.2)

        self.client.consume(record["id"])

        with self.assertRaises(OtpClientError):
            self.client.get_code("13777777777", wait=1.0, interval=0.2)

    def test_consume_failure_does_not_raise(self):
        # 消费不存在的 id：客户端应只记日志，不向用例抛异常
        self.client.consume(99999)


if __name__ == "__main__":
    unittest.main()
