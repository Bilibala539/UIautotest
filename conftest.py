"""
pytest fixture 配置文件
提供全局的测试设置和清理
"""

import pytest
import os
import logging
from datetime import datetime
from appium import webdriver

# 导入配置
from config.appium_config import DESIRED_CAPABILITIES, APPIUM_SERVER_CONFIG
# 导入新的测试数据管理器
from config.user_data import UserManager

# 配置日志
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{log_dir}/test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def appium_driver():
    """
    Session级别的driver fixture
    整个测试会话只启动一次Appium服务
    """
    driver = None
    try:
        logger.info("启动Appium WebDriver...")
        driver = webdriver.Remote(APPIUM_SERVER_CONFIG["url"], DESIRED_CAPABILITIES)
        driver.implicitly_wait(10)
        yield driver
    finally:
        if driver:
            logger.info("关闭Appium WebDriver...")
            driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    失败自动截图
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        driver = None
        # 尝试从测试函数参数中获取driver
        if hasattr(item, 'funcargs'):
            for arg_name, arg_value in item.funcargs.items():
                if hasattr(arg_value, 'get_screenshot_as_png'):
                    driver = arg_value
                    break

        if driver:
            screenshot_dir = "screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir,
                                           f"{item.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            driver.save_screenshot(screenshot_path)
            logger.info(f"失败截图已保存: {screenshot_path}")


def pytest_configure(config):
    """
    pytest配置
    """
    # 创建必要的目录
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    # 确保配置目录存在
    os.makedirs("config", exist_ok=True)


@pytest.fixture(scope="session")
def test_user_manager():
    return UserManager("config/users_info.json")
