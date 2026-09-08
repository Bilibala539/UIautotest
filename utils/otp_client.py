"""验证码平台（swan-otp-gateway）客户端。

供业务层（utils/aw/business/）轮询验证码，用例层不应直接使用。
网关地址通过环境变量 ``SWAN_OTP_GATEWAY`` 注入，例如::

    SWAN_OTP_GATEWAY=http://192.168.12.5:18080

网关为 pull 模式：调用 :meth:`OtpClient.get_code` 时，网关会主动请求
开发提供的 ``/user/captcha/mockCode`` 接口取码，客户端只需轮询即可。
"""
from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_GATEWAY_URL = "http://192.168.12.5:18080"


class OtpClientError(RuntimeError):
    """验证码获取或消费失败。"""


class OtpClient:
    """验证码网关 HTTP 客户端。

    Args:
        base_url: 网关地址，默认读环境变量 ``SWAN_OTP_GATEWAY``，
                  未设置时使用内网默认地址。
        request_timeout: 单次 HTTP 请求超时（秒）。
    """

    def __init__(self, base_url: str = "", request_timeout: float = 5.0):
        self.base_url = (
            base_url
            or os.environ.get("SWAN_OTP_GATEWAY", "").strip()
            or DEFAULT_GATEWAY_URL
        ).rstrip("/")
        self.request_timeout = request_timeout

    # ==================== 内部请求 ====================

    def _request(self, method: str, path: str, body: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=self.request_timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            raise OtpClientError(f"网关返回 HTTP {error.code}: {url}") from error
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            raise OtpClientError(f"请求验证码网关失败: {url} ({error})") from error

    # ==================== 对外接口 ====================

    def get_code(
        self,
        phone: str,
        wait: float = 60.0,
        interval: float = 2.0,
    ) -> Dict[str, Any]:
        """轮询获取指定手机号最新的可用验证码。

        网关 pull 模式下首次请求可能触发开发接口取码，需要轮询等待。

        Args:
            phone: 手机号。
            wait: 总等待时间（秒），超时抛 :class:`OtpClientError`。
            interval: 轮询间隔（秒）。

        Returns:
            网关返回的完整记录，验证码在 ``code`` 字段。
        """
        deadline = time.monotonic() + wait
        path = f"/api/test/otp/latest?phone={phone}"
        while True:
            try:
                record = self._request("GET", path)
                logger.info("获取到验证码: id=%s phone=%s", record.get("id"), phone)
                return record
            except OtpClientError:
                if time.monotonic() >= deadline:
                    raise OtpClientError(
                        f"等待验证码超时（{wait:.0f}s）: phone={phone}"
                    )
                time.sleep(interval)

    def consume(self, otp_id: int) -> None:
        """消费验证码，使其立即失效。失败不影响用例继续。"""
        try:
            self._request("POST", "/api/test/otp/consume", {"id": otp_id})
        except OtpClientError as error:
            logger.warning("消费验证码失败（忽略）: %s", error)
