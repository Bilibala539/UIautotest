"""
MuMu (Android) 端业务方法

包含 MuMu 模拟器上 POPO 应用的完整业务操作流程。
UI 流程、检查图片、操作步骤均为 Android 端专属。
"""
import logging
import subprocess
import time

from image.image_name_mapping import *
from utils.aw.business.common import CommonBusiness
from utils.aw.driver.base_driver import BasePlatformDriver
from utils.aw.search_region import Normal

logger = logging.getLogger(__name__)

POPO_PACKAGE = "com.netease.popo"
POPO_ACTIVITY = "com.netease.popo.MainActivity"


def _get_adb_path() -> str:
    from utils.devices import ADB_PATH
    return ADB_PATH


class MuMuBusiness(CommonBusiness):
    """
    MuMu (Android) 端业务类

    继承链: MuMuBusiness → CommonBusiness → AWBase
    """

    def __init__(self, driver: BasePlatformDriver):
        super().__init__(driver)
        from utils.devices import get_device_port_by_instance
        self._device_port = get_device_port_by_instance(driver.instance_id)
        self._device_serial = f"127.0.0.1:{self._device_port}"

    # ==================== ADB 命令 ====================

    def _run_adb_command(self, *args) -> bool:
        """执行ADB命令"""
        cmd = [_get_adb_path(), "-s", self._device_serial] + list(args)
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.error(f"❌ ADB命令超时: {' '.join(cmd)}")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ ADB命令失败: {e.stderr.decode()}")
            return False

    # ==================== 应用控制 ====================

    def start_app(self):
        """点击 MuMu 桌面上的 POPO 图标启动应用"""
        self.click_image(HOME_POPO_LOGO)

    def stop_app(self, package: str = POPO_PACKAGE) -> bool:
        """停止应用"""
        logger.info(f"📱 正在停止应用 {package}...")
        self._run_adb_command("shell", "am", "force-stop", package)
        time.sleep(0.5)
        logger.info("✅ 应用已停止")
        return True

    def restart_app(self) -> bool:
        """重启应用"""
        self.stop_app()
        time.sleep(1)
        self.start_app()
        return True

    def clear_app_data(self, package: str = POPO_PACKAGE) -> bool:
        """清除应用数据"""
        logger.info(f"🗑️ 正在清除应用数据 {package}...")
        self._run_adb_command("shell", "pm", "clear", package)
        time.sleep(1)
        logger.info("✅ 应用数据已清除")
        return True

    def page_ctrl(self):
        pass

    # ==================== 登录 / 退登 ====================

    def login(self, uid: str, password: str):
        """
        MuMu 端登录流程

        步骤:
        1. 点击桌面 POPO 图标启动应用
        2. 等待登录页面
        3. 点击邮箱 Tab
        4. 输入邮箱
        5. 输入密码
        6. 勾选协议
        7. 点击登录按钮
        8. 处理弹窗
        """
        logger.info(f"🔐 [MuMu] 开始登录: {uid}")

        self.start_app()
        self.sleep(2)

        self.image_exists(LOGIN_POPO_TEXT, timeout=5)
        logger.info("📱 检测到登录页面")

        self.click_text("邮箱", timeout=3)
        self.sleep(0.5)

        self.click_text("输入邮箱", timeout=5)
        self.sleep(0.5)
        self.input_text(str(uid))
        self.click_text("邮箱", timeout=5, dx=50, dy=180)

        if self.click_text("输入密码", timeout=5):
            self.sleep(0.3)
            self.input_text(str(password))

        try:
            self.click_image(LOGIN_READ_CENTER_FALSE)
            self.sleep(0.3)
            self.click_image(LOGIN_ENTER)
            self.sleep(1.5)
            self.image_exists(MESSAGE_TAB_BLUE, timeout=10)
        except:
            self.image_exists(LOGIN_READ_CENTER_TRUE)
            self.click_image(LOGIN_ENTER)
            self.sleep(1.5)
            self.image_exists(MESSAGE_TAB_BLUE, timeout=10)

        self.pop_not_allowed()
        logger.info(f"✅ [MuMu] 登录成功: {uid}")

    def logout(self) -> bool:
        """MuMu 端退出登录流程"""
        logger.info("🚪 [MuMu] 开始退出登录")
        try:
            self.click_image(MESSAGE_TAB_BLUE)
        except:
            self.click_image(MESSAGE_TAB_GRUE)

        self.click_image(MESSAGE_TAB_MSG_TEXT, dx=-70)
        time.sleep(0.3)
        self.click_image(SIDEBAR_SETTINGS)
        time.sleep(0.3)
        self.click_image(SETTINGS_LOGOUT)
        time.sleep(0.3)
        self.click_image(SETTINGS_LOGOUT_CONFIRM)
        time.sleep(1.5)
        self.image_exists(LOGIN_POPO_TEXT)
        logger.info("✅ [MuMu] 退出登录成功")
        return True

    # ==================== 弹窗处理 ====================

    def pop_not_allowed(self):
        self.pop_is_exisit(isallow=False)

    def pop_allowed(self):
        self.pop_is_exisit(isallow=True)

    def pop_is_exisit(self, isallow=False):
        try:
            self.image_exists(POPO_POP)
            time.sleep(0.5)
            if not isallow:
                self.click_image(POPO_POP_CANCEL)
                logger.info("弹窗已关闭")
        except:
            logger.info("未发现弹窗")

    # ==================== 群组相关 ====================

    def create_team(self):
        """创建群组"""
        username = "grp.popoqa"
        self.click_image(SESSIONLIST_PLUS_BUTTON)
        time.sleep(5)
        self.click_image(SESSIONLIST_PLUS_BUTTON_CREATETEAM)
        time.sleep(0.3)
        self.image_exists(SELECT_TITLE_ADD_TEAM_MUNBER)
        self.click_image(SELECT_SEARCH)
        self.input_text(str(username))
        time.sleep(1)

        self.click_image(SELECT_CIRCLE, region=Normal.HALF_UP)
        time.sleep(0.3)
        self.image_exists(SELECT_CIRCLE_BLUE, region=Normal.HALF_UP)
        self.click_image(SELECT_OK_BLUE, region=Normal.HALF_DOWN)

        try:
            self.text_exists(text="选择已有群组", region=Normal.HALF_UP)
            self.click_image(CREATE_NEW_TEAM, region=Normal.HALF_DOWN)
        except:
            pass

        self.text_exists(text="发起群聊", region=Normal.HALF_UP)
        self.text_exists(text="并邀请", region=Normal.HALF_UP)
        self.text_exists(text="加入群聊", region=Normal.HALF_UP)
        return True

    def delete_team(self):
        pass

    # ==================== 搜索相关 ====================
    def search(self, tab="全部", text=""):
        """创建群组"""

        self.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        self.image_exists(SEARCH_EMPTY)
        self.input_text(str(text))

        if tab in ["全部", "联系人", "群", "消息", "日程"]:
            self.click_text(tab)
            time.sleep(0.3)
            if tab is "全部":
                self.image_exists(SEARCH_TAB1, region=Normal.HALF_UP)
            elif tab is "联系人":
                self.image_exists(SEARCH_TAB2, region=Normal.HALF_UP)
            elif tab is "群":
                self.image_exists(SEARCH_TAB3, region=Normal.HALF_UP)
            elif tab is "消息":
                self.image_exists(SEARCH_TAB4, region=Normal.HALF_UP)
            elif tab is "日程":
                self.image_exists(SEARCH_TAB5, region=Normal.HALF_UP)



        else:
            # 云空间、任务、应用
            pass
