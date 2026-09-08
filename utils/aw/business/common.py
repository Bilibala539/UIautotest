"""跨项目公共业务 Mixin。

只做 Mixin，不继承 AWBase——业务类通过
``class XxxBusiness(CommonBusinessMixin, 某端BaseAW)`` 组合使用，
Mixin 里的 ``self.xxx`` 在运行时命中端 base / 公共引擎的方法。

验证码等纯 HTTP 依赖走 utils/ 独立客户端，不进基础 AW 层。
"""
from __future__ import annotations

import os
from typing import Optional

from utils.otp_client import OtpClient


class CommonBusinessMixin:
    """跨项目通用的业务方法（Mixin）。"""

    _otp_client: Optional[OtpClient] = None

    @property
    def otp(self) -> OtpClient:
        """验证码客户端（懒加载，全局共享一个实例）。"""
        if CommonBusinessMixin._otp_client is None:
            CommonBusinessMixin._otp_client = OtpClient()
        return CommonBusinessMixin._otp_client

    # ==================== 通用等待 ====================

    def wait_text(self, *texts: str, timeout: int = 10) -> bool:
        """等待任意一个文本出现，常用于断言页面到达。"""
        return any(
            self.find_text_by_ocr(text, timeout=timeout) is not None
            for text in texts
        )

    # ==================== 通用登录辅助 ====================

    def _sms_phone(self) -> str:
        """从环境变量读取当前账号手机号。"""
        return os.environ.get("SWAN_PHONE", "").strip()

    def _fetch_sms_code(self, phone: str, wait: float = 60.0) -> str:
        """触发取码后轮询验证码平台，返回验证码字符串。"""
        record = self.otp.get_code(phone, wait=wait)
        return str(record.get("code", ""))
