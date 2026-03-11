"""
高级AW方法 - 业务流程
基于中级AW，封装完整的业务操作流程

这些方法封装了完整的业务场景，如：
- login: 登录流程
- logout: 退出登录
- send_message: 发送消息
- create_team: 创建团队
"""
import logging
import subprocess
import time
from typing import Optional

from image.image_name_mapping import *
from utils.aw.aw_action import AWAction
from utils.devices import ADB_PATH, get_device_port_by_instance

logger = logging.getLogger(__name__)

# 网易POPO应用配置
POPO_PACKAGE = "com.netease.popo"
POPO_ACTIVITY = "com.netease.popo.MainActivity"


class AWBusiness(AWAction):
    """
    高级AW类 - 业务流程
    
    继承自AWAction，封装完整的业务操作流程：
    - start_app: 启动应用
    - login: 登录
    - logout: 退出登录
    - send_message: 发送消息
    """

    def __init__(self, instance_id: int):
        """
        初始化高级AW
        
        Args:
            instance_id: MuMu模拟器实例ID (0, 1, 2...)
        """
        super().__init__(instance_id)

        # 获取对应实例的ADB端口用于应用控制
        self.device_port = get_device_port_by_instance(instance_id)
        self.device_serial = f"127.0.0.1:{self.device_port}"

    def _run_adb_command(self, *args) -> bool:
        """
        执行ADB命令（仅用于应用控制）
        
        Args:
            *args: ADB命令参数
            
        Returns:
            bool: 命令是否成功
        """
        cmd = [ADB_PATH, "-s", self.device_serial] + list(args)
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"❌ ADB命令执行失败: {e}")
            return False

    # ==================== 应用控制 ====================

    def start_app(self):
        """
        启动应用
        """
        self.click_image(HOME_POPO_LOGO)

    def stop_app(self, package: str = POPO_PACKAGE) -> bool:
        """
        停止应用
        
        Args:
            package: 应用包名
            
        Returns:
            bool: 停止是否成功
        """
        try:
            logger.info(f"📱 正在停止应用 {package}...")
            self._run_adb_command("shell", "am", "force-stop", package)
            time.sleep(0.5)
            logger.info(f"✅ 应用已停止")
            return True
        except Exception as e:
            logger.error(f"❌ 应用停止失败: {e}")
            return False

    def restart_app(self, package: str = POPO_PACKAGE, activity: str = POPO_ACTIVITY) -> bool:
        """
        重启应用
        
        Args:
            package: 应用包名
            activity: 启动Activity
            
        Returns:
            bool: 重启是否成功
        """
        self.stop_app(package)
        time.sleep(1)
        return self.start_app(package, activity)

    def clear_app_data(self, package: str = POPO_PACKAGE) -> bool:
        """
        清除应用数据
        
        Args:
            package: 应用包名
            
        Returns:
            bool: 清除是否成功
        """
        try:
            logger.info(f"🗑️ 正在清除应用数据 {package}...")
            self._run_adb_command("shell", "pm", "clear", package)
            time.sleep(1)
            logger.info(f"✅ 应用数据已清除")
            return True
        except Exception as e:
            logger.error(f"❌ 清除数据失败: {e}")
            return False

    # ==================== 登录相关 ====================

    def login(self, uid: str, password: str) -> bool:
        """
        执行登录流程
        
        步骤:
        1. 启动POPO应用
        2. 等待登录页面加载
        3. 点击邮箱Tab
        4. 输入邮箱
        5. 输入密码
        6. 勾选协议（如需要）
        7. 点击登录按钮
        8. 等待登录完成
        
        Args:
            uid: 用户邮箱
            password: 密码
            
        Returns:
            bool: 登录是否成功
        """
        logger.info(f"🔐 开始登录: {uid}")

        # 启动应用
        self.start_app()
        self.sleep(2)

        # 检查是否在登录页面
        self.image_exists(LOGIN_POPO_TEXT, timeout=5)
        logger.info("📱 检测到登录页面，开始输入登录信息")

        # 点击邮箱Tab（确保在邮箱登录模式）
        self.click_text("邮箱", timeout=3)
        self.sleep(0.5)

        # 输入邮箱
        self.click_text("输入邮箱", timeout=5)
        self.sleep(0.5)
        self.input_text(str(uid))
        self.click_text("邮箱", timeout=5, dx=50, dy=180)  # 点击输入框下方的联想提示

        # 输入密码
        if self.click_text("输入密码", timeout=5):
            self.sleep(0.3)
            self.input_text(str(password))

        # 勾选协议（如果存在且未勾选）
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

        # 检查是否有弹窗
        self.pop_not_allowed()

    def logout(self) -> bool:
        """
        执行退出登录流程
        
        Returns:
            bool: 退出是否成功
        """
        logger.info("🚪 开始退出登录")
        try:
            self.click_image(MESSAGE_TAB_BLUE)


        except:
            self.click_image(MESSAGE_TAB_GRUE)

        self.click_image(MESSAGE_TAB_MSG_TEXT, dx=-70)  # 点击头像
        time.sleep(0.3)
        self.click_image(SIDEBAR_SETTINGS)
        time.sleep(0.3)
        self.click_image(SETTINGS_LOGOUT)
        time.sleep(0.3)
        self.click_image(SETTINGS_LOGOUT_CONFIRM)
        time.sleep(1.5)
        self.image_exists(LOGIN_POPO_TEXT)
        logger.info("✅ 退出登录成功")
        return True

    # ==================== 消息相关 ====================

    def send_p2p_message(self, recipient: str, message: str) -> bool:
        """
        发送消息
        
        Args:
            recipient: 接收者名称
            message: 消息内容
            
        Returns:
            bool: 发送是否成功
        """
        logger.info(f"📤 发送消息给 {recipient}: {message}")

        # TODO: 实现发送消息的具体流程
        # 1. 搜索/点击联系人
        # 2. 进入聊天窗口
        # 3. 输入消息
        # 4. 点击发送

        return True

    # ==================== 团队相关 ====================

    def create_team(self, team_name: str) -> bool:
        """
        创建团队
        
        Args:
            team_name: 团队名称
            
        Returns:
            bool: 创建是否成功
        """
        logger.info(f"👥 创建团队: {team_name}")

        # TODO: 实现创建团队的具体流程

        return True

    # ==================== 页面导航 ====================

    def go_to_home(self) -> bool:
        """
        返回首页
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("🏠 返回首页")
        # 多次按返回键确保回到首页
        for _ in range(5):
            self.press_back()
            self.sleep(0.3)
        return True

    def go_to_contacts(self) -> bool:
        """
        进入联系人页面
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("📇 进入联系人页面")
        return self.click_text("联系人", timeout=5)

    def go_to_messages(self) -> bool:
        """
        进入消息页面
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("💬 进入消息页面")
        return self.click_text("消息", timeout=5)

    def go_to_settings(self) -> bool:
        """
        进入设置页面
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("⚙️ 进入设置页面")
        # 通常需要点击"我的"或头像，然后点击设置
        return self.click_text("设置", timeout=5)

    def pop_not_allowed(self):
        self.pop_is_exisit(isallow=False)

    def pop_allowed(self):
        self.pop_is_exisit(isallow=True)

    def pop_is_exisit(self, isallow=False):
        try:
            self.image_exists(POPO_POP)
            time.sleep(0.5)
            if isallow:
                pass
                # todo授权弹窗
            else:
                self.click_image(POPO_POP_CANCEL)
                logger.info("弹窗已关闭")

        except:
            logger.info("未发现弹窗")
