import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from scripts.otp_gateway.server import create_server


class OtpGatewayTest(unittest.TestCase):
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
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp_directory.cleanup()

    def request(self, method, path, token, body=None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def test_receive_read_and_consume(self):
        status, created = self.request(
            "POST",
            "/api/test/otp",
            "ingest-secret",
            {
                "phone": "13777777777",
                "code": "123456",
            },
        )
        self.assertEqual(status, 201)
        self.assertNotIn("code", created)

        status, record = self.request(
            "GET",
            "/api/test/otp/latest?phone=13777777777",
            "read-secret",
        )
        self.assertEqual(status, 200)
        self.assertEqual(record["code"], "123456")
        self.assertEqual(record["phone"], "13777777777")

        status, consumed = self.request(
            "POST",
            "/api/test/otp/consume",
            "read-secret",
            {"id": record["id"]},
        )
        self.assertEqual(status, 200)
        self.assertTrue(consumed["consumed"])
        self.assertEqual(
            self.request(
                "GET",
                "/api/test/otp/latest?phone=13777777777",
                "read-secret",
            )[0],
            404,
        )
        status, recent = self.request("GET", "/api/test/otp/recent?limit=10", "")
        self.assertEqual(status, 200)
        self.assertEqual(recent["items"][0]["status"], "consumed")

    def test_auth_and_account_allowlist(self):
        self.assertEqual(
            self.request(
                "POST",
                "/api/test/otp",
                "wrong",
                {"phone": "13777777777", "code": "1234"},
            )[0],
            401,
        )
        self.assertEqual(
            self.request(
                "POST",
                "/api/test/otp",
                "ingest-secret",
                {"phone": "13888888888", "code": "1234"},
            )[0],
            403,
        )

    def test_read_api_is_open_by_default(self):
        self.request(
            "POST",
            "/api/test/otp",
            "ingest-secret",
            {"phone": "13777777777", "code": "654321"},
        )
        status, record = self.request(
            "GET",
            "/api/test/otp/latest?phone=13777777777",
            "",
        )
        self.assertEqual(status, 200)
        self.assertEqual(record["code"], "654321")
        status, recent = self.request("GET", "/api/test/otp/recent?limit=10", "")
        self.assertEqual(status, 200)
        self.assertEqual(len(recent["items"]), 1)

    def test_ingest_is_open_by_default(self):
        open_server = create_server(
            "127.0.0.1",
            0,
            Path(self.temp_directory.name) / "open.sqlite3",
            "",
            "",
        )
        thread = threading.Thread(target=open_server.serve_forever, daemon=True)
        thread.start()
        try:
            base_url = f"http://127.0.0.1:{open_server.server_address[1]}"
            request = urllib.request.Request(
                base_url + "/api/test/otp",
                data=json.dumps({"phone": "13777777777", "code": "654321"}).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(request) as response:
                self.assertEqual(response.status, 201)
        finally:
            open_server.shutdown()
            open_server.server_close()
            thread.join(timeout=2)

    def test_latest_fetches_code_from_configured_captcha_source(self):
        requested_phones = []

        class CaptchaSourceHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                requested_phones.append(parse_qs(urlparse(self.path).query).get("tel", [""])[0])
                payload = json.dumps({"data": {"mockCode": "998877"}}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, format_string, *args):
                return

        source_server = ThreadingHTTPServer(("127.0.0.1", 0), CaptchaSourceHandler)
        source_thread = threading.Thread(target=source_server.serve_forever, daemon=True)
        source_thread.start()
        gateway = create_server(
            "127.0.0.1",
            0,
            Path(self.temp_directory.name) / "source.sqlite3",
            "",
            "",
            captcha_source_url=f"http://127.0.0.1:{source_server.server_address[1]}/user/captcha/mockCode",
        )
        gateway_thread = threading.Thread(target=gateway.serve_forever, daemon=True)
        gateway_thread.start()
        try:
            base_url = f"http://127.0.0.1:{gateway.server_address[1]}"
            with urllib.request.urlopen(
                f"{base_url}/api/test/otp/latest?phone=13666666666"
            ) as response:
                record = json.loads(response.read())
            self.assertEqual(record["code"], "998877")
            self.assertEqual(record["phone"], "13666666666")
            self.assertEqual(requested_phones, ["13666666666"])
            with urllib.request.urlopen(f"{base_url}/api/test/otp/recent?limit=10") as response:
                recent = json.loads(response.read())
            self.assertEqual(recent["items"][0]["code"], "998877")
        finally:
            gateway.shutdown()
            gateway.server_close()
            gateway_thread.join(timeout=2)
            source_server.shutdown()
            source_server.server_close()
            source_thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
