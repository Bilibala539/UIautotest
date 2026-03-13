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

    # ==================== 群组相关 ====================

    # 创建群组，选择成员后创建新群聊
    def create_group(self, member_names: list) -> bool:
        """
        创建群组
        
        流程:
        1. 确保在消息tab页
        2. 点击右上角"+"按钮
        3. 点击"创建群组"
        4. 在选人组件中选择成员（支持会话/联系人/群组tab）
        5. 点击"确定"按钮
        6. 如果出现"已有群组"推荐页面，点击"创建新的群组"
        7. 等待进入新群聊界面
        
        Args:
            member_names: 群成员名称列表
            
        Returns:
            bool: 创建是否成功
        """
        logger.info(f"👥 创建群组，成员: {member_names}")
        
        # 1. 确保在消息tab页
        try:
            self.click_image(MESSAGE_TAB_BLUE, timeout=2)
        except:
            self.click_image(MESSAGE_TAB_GRUE, timeout=2)
        self.sleep(0.5)
        
        # 2. 点击右上角"+"按钮
        self.click_text("+", timeout=3)
        self.sleep(0.5)
        
        # 3. 点击"创建群组"
        self.click_text("创建群组", timeout=3)
        self.sleep(1)
        
        # 4. 选择群成员
        # 确认进入添加群成员页面
        self.text_exists("添加群成员", timeout=5)
        
        for name in member_names:
            # 点击成员名称进行选择
            if self.click_text(name, timeout=3):
                logger.info(f"✅ 已选择成员: {name}")
                self.sleep(0.3)
            else:
                logger.warning(f"⚠️ 未找到成员: {name}")
        
        self.sleep(0.5)
        
        # 5. 点击"确定"按钮
        self.click_text("确定", timeout=3)
        self.sleep(1.5)
        
        # 6. 处理"选择已有群组"页面（如果出现）
        if self.text_exists("选择已有群组", timeout=2):
            logger.info("📋 检测到已有群组推荐页面，选择创建新群组")
            self.click_text("创建新的群组", timeout=3)
            self.sleep(1.5)
        
        # 7. 验证是否进入群聊界面
        if self.text_exists("名群成员", timeout=5):
            logger.info("✅ 群组创建成功")
            return True
        else:
            logger.error("❌ 群组创建失败")
            return False

    # 进入指定群聊
    def enter_group(self, group_name: str) -> bool:
        """
        进入指定群聊
        
        流程:
        1. 确保在消息tab页
        2. 在会话列表中点击群聊名称
        3. 等待进入群聊界面
        
        Args:
            group_name: 群聊名称
            
        Returns:
            bool: 是否成功进入
        """
        logger.info(f"📥 进入群聊: {group_name}")
        
        # 1. 确保在消息tab页
        try:
            self.click_image(MESSAGE_TAB_BLUE, timeout=2)
        except:
            self.click_image(MESSAGE_TAB_GRUE, timeout=2)
        self.sleep(0.5)
        
        # 2. 点击群聊
        if self.click_text(group_name, timeout=5):
            self.sleep(1)
            # 3. 验证是否进入群聊界面
            if self.text_exists("名群成员", timeout=3):
                logger.info(f"✅ 成功进入群聊: {group_name}")
                return True
        
        logger.error(f"❌ 未找到群聊: {group_name}")
        return False

    # 打开当前群聊的群设置页面
    def open_group_settings(self) -> bool:
        """
        打开群设置页面
        
        前置条件: 当前在群聊界面
        
        流程:
        1. 点击顶部群名称区域
        2. 等待群设置页面加载
        
        Returns:
            bool: 是否成功打开
        """
        logger.info("⚙️ 打开群设置")
        
        # 点击群名称进入设置（群名称在顶部中央）
        # 通过点击"名群成员"文字上方区域
        if self.click_text("名群成员", timeout=3, dy=-30):
            self.sleep(1)
            # 验证是否进入群设置页面
            if self.text_exists("设置", timeout=3) and self.text_exists("群成员", timeout=3):
                logger.info("✅ 成功打开群设置")
                return True
        
        logger.error("❌ 打开群设置失败")
        return False

    # 退出当前群组
    def exit_group(self) -> bool:
        """
        退出群组
        
        前置条件: 当前在群聊界面或群设置页面
        
        流程:
        1. 如果不在群设置页面，先打开群设置
        2. 向上滑动到页面底部
        3. 点击"退出群组"按钮
        4. 确认退出（如有确认弹窗）
        
        Returns:
            bool: 退出是否成功
        """
        logger.info("🚪 退出群组")
        
        # 1. 如果不在群设置页面，尝试打开
        if not self.text_exists("群成员", timeout=2):
            self.open_group_settings()
        
        # 2. 向上滑动找到"退出群组"按钮
        max_swipes = 3
        for i in range(max_swipes):
            if self.text_exists("退出群组", timeout=2):
                break
            self.swipe_up()
            self.sleep(0.5)
        
        # 3. 点击"退出群组"
        if self.click_text("退出群组", timeout=3):
            self.sleep(0.5)
            
            # 4. 处理确认弹窗（如果有）
            if self.text_exists("确定", timeout=2):
                self.click_text("确定", timeout=2)
                self.sleep(1)
            
            # 验证退出成功（应该回到消息列表）
            if self.text_exists("消息", timeout=5):
                logger.info("✅ 成功退出群组")
                return True
        
        logger.error("❌ 退出群组失败")
        return False

    # 在当前群聊中发送消息
    def send_group_message(self, message: str) -> bool:
        """
        在当前群聊发送消息
        
        前置条件: 当前在群聊界面
        
        Args:
            message: 消息内容
            
        Returns:
            bool: 发送是否成功
        """
        logger.info(f"📤 发送群消息: {message}")
        
        # 点击输入框区域（底部"发送"按钮左侧）
        if self.click_text("发送", timeout=3, dx=-150):
            self.sleep(0.3)
            # 输入消息
            self.input_text(message)
            self.sleep(0.3)
            # 点击发送
            self.click_text("发送", timeout=3)
            self.sleep(0.5)
            logger.info("✅ 消息发送成功")
            return True
        
        logger.error("❌ 消息发送失败")
        return False

    # 在群聊中@某个成员
    def at_group_member(self, member_name: str, message: str = "") -> bool:
        """
        @群成员
        
        前置条件: 当前在群聊界面
        
        流程:
        1. 点击底部工具栏的@按钮
        2. 选择要@的成员
        3. 输入附加消息（可选）
        4. 发送
        
        Args:
            member_name: 成员名称
            message: 附加消息内容
            
        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📢 @成员: {member_name}")
        
        # 点击底部工具栏的@按钮
        self.tap(313, 928)  # @按钮的位置（根据截图）
        self.sleep(0.5)
        
        # 选择成员
        if self.click_text(member_name, timeout=3):
            self.sleep(0.3)
            
            # 输入附加消息
            if message:
                self.input_text(message)
                self.sleep(0.3)
            
            # 发送
            self.click_text("发送", timeout=3)
            self.sleep(0.5)
            logger.info(f"✅ 成功@{member_name}")
            return True
        
        logger.error(f"❌ 未找到成员: {member_name}")
        return False

    # 添加成员到当前群组
    def add_group_member(self, member_names: list) -> bool:
        """
        添加群成员
        
        前置条件: 当前在群聊界面或群设置页面
        
        流程:
        1. 如果不在群设置页面，先打开群设置
        2. 点击群成员区域的"添加"按钮
        3. 选择要添加的成员
        4. 点击确定
        
        Args:
            member_names: 要添加的成员名称列表
            
        Returns:
            bool: 添加是否成功
        """
        logger.info(f"➕ 添加群成员: {member_names}")
        
        # 1. 如果不在群设置页面，尝试打开
        if not self.text_exists("群成员", timeout=2):
            self.open_group_settings()
        
        # 2. 点击"添加"按钮
        if self.click_text("添加", timeout=3):
            self.sleep(1)
            
            # 3. 选择成员
            for name in member_names:
                if self.click_text(name, timeout=3):
                    logger.info(f"✅ 已选择: {name}")
                    self.sleep(0.3)
                else:
                    logger.warning(f"⚠️ 未找到: {name}")
            
            # 4. 点击确定
            self.click_text("确定", timeout=3)
            self.sleep(1)
            
            logger.info("✅ 添加成员完成")
            return True
        
        logger.error("❌ 添加成员失败")
        return False

    # 设置群公告
    def set_group_notice(self, notice: str) -> bool:
        """
        设置群公告
        
        前置条件: 当前在群聊界面或群设置页面
        
        Args:
            notice: 公告内容
            
        Returns:
            bool: 设置是否成功
        """
        logger.info(f"📋 设置群公告: {notice}")
        
        # 如果不在群设置页面，先打开
        if not self.text_exists("群公告", timeout=2):
            self.open_group_settings()
            self.sleep(0.5)
        
        # 点击群公告入口
        if self.click_text("群公告", timeout=3):
            self.sleep(1)
            
            # 输入公告内容（具体实现根据实际页面结构调整）
            self.input_text(notice)
            self.sleep(0.3)
            
            # 点击发布/确定
            if self.click_text("发布", timeout=3) or self.click_text("确定", timeout=3):
                self.sleep(1)
                logger.info("✅ 群公告设置成功")
                return True
        
        logger.error("❌ 群公告设置失败")
        return False

    # 切换群消息提醒开关
    def toggle_group_notification(self, enable: bool = True) -> bool:
        """
        切换群消息提醒
        
        前置条件: 当前在群设置页面
        
        Args:
            enable: True开启提醒，False关闭提醒
            
        Returns:
            bool: 操作是否成功
        """
        action = "开启" if enable else "关闭"
        logger.info(f"🔔 {action}群消息提醒")
        
        # 如果不在群设置页面，先打开
        if not self.text_exists("消息提醒", timeout=2):
            self.open_group_settings()
            self.swipe_up()  # 滑动到消息提醒位置
            self.sleep(0.5)
        
        # 点击消息提醒开关
        if self.click_text("消息提醒", timeout=3, dx=200):
            self.sleep(0.5)
            logger.info(f"✅ 已{action}群消息提醒")
            return True
        
        logger.error(f"❌ {action}群消息提醒失败")
        return False
