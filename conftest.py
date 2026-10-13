"""Web 自动化测试的 pytest 配置、日志与浏览器 fixtures。"""
from __future__ import annotations

import base64
import logging
import os
import shutil
import subprocess
from datetime import datetime
from typing import Dict, Optional

import pytest
from dotenv import load_dotenv

from config.user_data import UserManager
from utils.aw.driver.android_driver import AndroidAdbDriver
from utils.aw.driver.flutter_driver import FlutterAndroidDriver
from utils.user import AndroidUser, SwanUser, TTUser

pytest_plugins = ["reporter.pytest_plugin"]  # 2026-10-13 平台分离:dashboard.pytest_plugin 迁至 reporter/(上报对留自动化仓)

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env.local"))
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_OUTPUT_DIR = os.path.join(_BASE_DIR, "output")
log_dir = os.path.join(_OUTPUT_DIR, "logs")
os.makedirs(log_dir, exist_ok=True)
_log_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(log_dir, f"test_{_log_timestamp}.html")
_HTML_HEADER = "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Test Log</title></head><body>\n"
_HTML_FOOTER = "</body></html>\n"


class HtmlFileHandler(logging.Handler):
    """将日志和截图写入独立 HTML 文件。"""

    def __init__(self, filepath: str):
        super().__init__()
        self._filepath = filepath
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(_HTML_HEADER)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
            safe_message = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            with open(self._filepath, "a", encoding="utf-8") as file:
                file.write(f"<div>{safe_message}</div>\n")
        except Exception:
            self.handleError(record)

    def append_screenshot(self, label: str, screenshot_path: str, img_b64: str = None) -> None:
        try:
            if img_b64 is None:
                with open(screenshot_path, "rb") as image_file:
                    img_b64 = base64.b64encode(image_file.read()).decode("utf-8")
            with open(self._filepath, "a", encoding="utf-8") as file:
                file.write(f'<div><strong>{label}</strong><br><img src="data:image/png;base64,{img_b64}" style="max-width:100%"></div>\n')
        except Exception:
            pass

    def close(self) -> None:
        try:
            with open(self._filepath, "a", encoding="utf-8") as file:
                file.write(_HTML_FOOTER)
        finally:
            super().close()


root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
root_logger.addHandler(console_handler)
logger = logging.getLogger(__name__)
_per_test_html_handler: Optional[HtmlFileHandler] = None
_per_test_log_file: Optional[str] = None


def _get_platform() -> str:
    platform = os.environ.get("PLATFORM", "web").strip().lower()
    if platform not in {"web", "android", "flutter"}:
        raise ValueError("PLATFORM 仅支持 web、android 或 flutter")
    return platform


def _cleanup_intermediate_screenshots() -> None:
    screenshot_dir = os.path.join(_OUTPUT_DIR, "screenshots")
    if not os.path.isdir(screenshot_dir):
        return
    for filename in os.listdir(screenshot_dir):
        if filename.startswith(("failed_ocr_", "failed_find_")):
            try:
                os.remove(os.path.join(screenshot_dir, filename))
            except OSError:
                pass


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session) -> None:
    """环境门禁(③ preflight)+ 设备池领取(P3):仅 flutter/android 平台。"""
    if os.environ.get("PREFLIGHT", "").strip() in {"1", "true", "True", "on"}:
        from qa_platform.preflight import run_preflight
        verdict = run_preflight()
        for item in verdict["results"]:
            mark = "✅" if item["ok"] else ("🚫 阻塞" if item["blocking"] else "⚠️ 非阻塞")
            logger.info(f"[preflight] {mark} {item['check']}: {item['detail']}")
        if verdict["verdict"] == "ENV_BLOCKED":
            blocked = ", ".join(verdict["blocked_by"])
            logger.error(f"[preflight] 环境阻塞({blocked}),会话终止。环境问题按 bug 处理。")
            pytest.exit(f"环境门禁未通过: {blocked}", returncode=3)

    # 设备池:平台会话(有 DASHBOARD_URL)且未显式关闭(DEVICE_POOL=0)时启用
    _platform_now = os.environ.get("PLATFORM", "web").strip().lower()
    _pool_enabled = (
        _platform_now in {"flutter", "android"}
        and os.environ.get("DASHBOARD_URL", "").strip()
        and os.environ.get("DEVICE_POOL", "1").strip() not in {"0", "false", "off"}
        and not os.environ.get("ANDROID_DEVICE_SERIAL", "").strip()  # 手动指定串号时不抢池
    )
    if _pool_enabled:
        from qa_platform.device_pool import DevicePoolError, DevicePoolSession, register_local_devices
        try:
            register_local_devices(platform=_platform_now)
        except DevicePoolError as error:
            logger.warning(f"[device-pool] 设备注册失败(不影响会话): {error}")
        run_id = os.environ.get("DASHBOARD_RUN_ID") or f"pool-{_log_timestamp}"
        os.environ["DASHBOARD_RUN_ID"] = run_id
        global _device_pool
        _device_pool = DevicePoolSession(platform=_platform_now, run_id=run_id)
        try:
            serial = _device_pool.acquire()
            logger.info(f"[device-pool] 已领取设备: {serial}(会话 {run_id})")
        except DevicePoolError as error:
            logger.error(f"[device-pool] 无可领设备: {error}")
            pytest.exit(f"设备池无空闲设备: {error}", returncode=3)


_device_pool = None  # 当前会话的设备池领取对象(见 pytest_sessionstart)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item) -> None:
    global _per_test_html_handler, _per_test_log_file
    stem = os.path.splitext(os.path.basename(str(item.fspath)))[0]
    _per_test_log_file = os.path.join(log_dir, f"{stem}.html")
    _per_test_html_handler = HtmlFileHandler(_per_test_log_file)
    _per_test_html_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    root_logger.addHandler(_per_test_html_handler)


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item, nextitem) -> None:
    global _per_test_html_handler, _per_test_log_file
    if _per_test_html_handler is not None:
        root_logger.removeHandler(_per_test_html_handler)
        _per_test_html_handler.close()
        _per_test_html_handler = None
        _per_test_log_file = None


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.passed:
        _cleanup_intermediate_screenshots()


def _create_browser():
    from selenium import webdriver
    browser_name = os.environ.get("WEB_BROWSER", "chrome").strip().lower()
    headless = os.environ.get("WEB_HEADLESS", "0") == "1"
    width = int(os.environ.get("WEB_VIEWPORT_WIDTH", "1440"))
    height = int(os.environ.get("WEB_VIEWPORT_HEIGHT", "900"))
    if browser_name == "chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={width},{height}")
        return webdriver.Chrome(options=options)
    if browser_name == "edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={width},{height}")
        return webdriver.Edge(options=options)
    if browser_name == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        browser = webdriver.Firefox(options=options)
        browser.set_window_size(width, height)
        return browser
    raise ValueError("WEB_BROWSER 仅支持 chrome、edge 或 firefox")


@pytest.fixture(scope="function")
def browser():
    if _get_platform() != "web":
        raise RuntimeError("当前平台不会启动浏览器；请使用 users/tt_user fixture")
    web_browser = _create_browser()
    base_url = os.environ.get("WEB_BASE_URL", "").strip()
    if base_url:
        web_browser.get(base_url)
    yield web_browser
    web_browser.quit()


class TTUsersFactory:
    """为同一浏览器会话按名称缓存 TidiTree 测试用户。"""

    def __init__(self, browser=None, driver=None, user_cls=TTUser):
        if browser is not None and driver is not None:
            raise ValueError("browser 与 driver 只能传入一个")
        if browser is None and driver is None:
            raise ValueError("必须传入 browser 或 driver")
        self._browser = browser
        self._driver = driver
        self._user_cls = user_cls
        self._created_users: Dict[str, TTUser] = {}

    def __call__(self, user_key: str = "default", **kwargs) -> TTUser:
        if user_key not in self._created_users:
            env_key = user_key.upper().replace("-", "_")
            self._created_users[user_key] = self._user_cls(
                browser=self._browser,
                username=kwargs.get("username", os.environ.get(f"TT_{env_key}_USERNAME", "")),
                password=kwargs.get("password", os.environ.get(f"TT_{env_key}_PASSWORD", "")),
                name=kwargs.get("name", user_key),
                driver=self._driver,
            )
        return self._created_users[user_key]


class BaseTest:
    """Web 测试基类；在 ``setup`` 中通过 ``self.users()`` 获取 ``TTUser``。"""
    users: TTUsersFactory


@pytest.fixture(scope="function")
def users(request) -> TTUsersFactory:
    if _get_platform() == "web":
        return TTUsersFactory(browser=request.getfixturevalue("browser"))
    driver_class = FlutterAndroidDriver if _get_platform() == "flutter" else AndroidAdbDriver
    # 按项目分发用户类：web=TidiTree、flutter=Swan、android=智能音箱屏项目
    user_cls = {"flutter": SwanUser, "android": AndroidUser}.get(_get_platform(), TTUser)
    return TTUsersFactory(driver=driver_class(), user_cls=user_cls)


@pytest.fixture(scope="function")
def tt_user(request) -> TTUser:
    if _get_platform() == "web":
        return TTUser(browser=request.getfixturevalue("browser"))
    driver_class = FlutterAndroidDriver if _get_platform() == "flutter" else AndroidAdbDriver
    user_cls = {"flutter": SwanUser, "android": AndroidUser}.get(_get_platform(), TTUser)
    return user_cls(driver=driver_class())


@pytest.fixture(scope="function")
def aw(tt_user):
    return tt_user.aw


@pytest.fixture(scope="function", autouse=True)
def _auto_test_lifecycle(request):
    instance = request.instance
    if not isinstance(instance, BaseTest):
        yield
        return
    instance.users = request.getfixturevalue("users")
    if hasattr(instance, "setup") and callable(instance.setup):
        instance.setup()
    yield
    if hasattr(instance, "teardown") and callable(instance.teardown):
        instance.teardown()


@pytest.fixture(scope="session")
def test_user_manager():
    return UserManager(os.path.join(_BASE_DIR, "config", "users_info.json"))


# Swan 用例的平台/账号门禁集中处理（2026-10-13 用户拍板：用例文件里不写
# 模块级 _platform/_has_phone 探测与 pytestmark skipif，统一框架层过滤）
_SWAN_TESTS_DIR = os.path.join("tests", "flutter")
_PASSWORD_CASE_STEMS = {"test_登录页形态互切", "test_密码登录成功", "test_错误密码拒绝"}


def pytest_collection_modifyitems(config, items):
    platform = os.environ.get("PLATFORM", "web").strip().lower()
    has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())
    has_password = bool(os.environ.get("SWAN_PASSWORD", "").strip())
    for item in items:
        path = str(item.fspath)
        if _SWAN_TESTS_DIR not in path:
            continue
        if platform != "flutter":
            item.add_marker(pytest.mark.skip(
                reason=f"Swan 用例需要 PLATFORM=flutter（当前 {platform}）"))
        elif not has_phone:
            item.add_marker(pytest.mark.skip(reason="Swan 用例需要 SWAN_PHONE"))
        elif (os.path.splitext(os.path.basename(path))[0] in _PASSWORD_CASE_STEMS
              and not has_password):
            item.add_marker(pytest.mark.skip(reason="密码域用例需要 SWAN_PASSWORD"))


def pytest_sessionfinish(session, exitstatus) -> None:
    # 归还设备池里的设备(无论会话成败),再生成 Allure 报告
    if _device_pool is not None:
        _device_pool.release()
    _generate_allure_report()


def _generate_allure_report() -> None:
    allure_results = os.path.join(_OUTPUT_DIR, "allure-results")
    allure_report = os.path.join(_OUTPUT_DIR, "allure-report")
    if not os.path.isdir(allure_results):
        return
    with open(os.path.join(allure_results, "allure.properties"), "w", encoding="utf-8") as file:
        file.write("allure.report.language=zh\n")
    allure_cmd = shutil.which("allure") or shutil.which("allure.bat") or r"C:\tools\allure-2.27.0\bin\allure.bat"
    try:
        subprocess.run([allure_cmd, "generate", allure_results, "-o", allure_report, "--clean"], check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except (FileNotFoundError, subprocess.CalledProcessError):
        logger.warning("Allure CLI 未安装或报告生成失败，跳过本地报告生成")
