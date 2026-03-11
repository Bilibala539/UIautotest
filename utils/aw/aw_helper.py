"""
AW Helper - 用户调用入口
提供统一的AW方法调用接口，用户通过 user.aw.xxx() 方式调用

AWHelper 继承自 AWBusiness，包含所有层级的AW方法：
- 低级AW (AWBase): tap, input, press_key 等
- 中级AW (AWAction): click_text, click_image, input_text 等
- 高级AW (AWBusiness): login, logout, send_message 等

使用方式:
    user.aw = AWHelper(user.device.instance_id)
    user.aw.click_text("登录")
    user.aw.login(uid, password)
"""
import logging
from utils.aw.aw_business import AWBusiness

logger = logging.getLogger(__name__)


class AWHelper(AWBusiness):
    """
    AW帮助类 - 用户调用入口
    
    继承层级:
    AWHelper -> AWBusiness -> AWAction -> AWBase
    
    包含所有AW方法：
    
    低级AW (来自 AWBase):
        - tap(x, y): 点击坐标
        - long_press(x, y, duration): 长按
        - double_tap(x, y): 双击
        - swipe(...): 滑动
        - swipe_up/down/left/right(): 方向滑动
        - input(text): 输入文本（支持中文）
        - clear_input(length): 清空输入框
        - press_key(keycode): 按键
        - press_back/home/enter(): 常用按键
        - sleep(seconds): 等待
        - screenshot(filename): 截图
    
    中级AW (来自 AWAction):
        - find_text(text, timeout): 查找文本
        - click_text(text, timeout): 点击文本
        - long_press_text(text, duration, timeout): 长按文本
        - double_click_text(text, timeout): 双击文本
        - text_exists(text, timeout): 检查文本是否存在
        - wait_text(text, timeout): 等待文本出现
        - wait_text_disappear(text, timeout): 等待文本消失
        - get_screen_text(): 获取屏幕文本
        - input_text(label, value, timeout): 在标签输入框输入
        - find_image(template, threshold, timeout): 查找图像
        - click_image(template, threshold, timeout): 点击图像
        - long_press_image(...): 长按图像
        - image_exists(template, threshold, timeout): 检查图像是否存在
        - wait_image(template, threshold, timeout): 等待图像出现
        - assert_text_not_exists(): 断言文本不存在
        - assert_image_not_exists(): 断言图像不存在
    
    高级AW (来自 AWBusiness):
        - start_app(package, activity): 启动应用
        - stop_app(package): 停止应用
        - restart_app(package, activity): 重启应用
        - clear_app_data(package): 清除应用数据
        - login(uid, password): 登录
        - logout(): 退出登录
        - send_message(recipient, message): 发送消息
        - create_team(team_name): 创建团队
        - go_to_home/contacts/messages/settings(): 页面导航
    
    使用示例:
        # 在PPUser类中
        self.aw = AWHelper(self.device.instance_id)
        
        # 低级操作
        self.aw.tap(100, 200)
        self.aw.input("hello")
        
        # 中级操作
        self.aw.click_text("登录")
        self.aw.input_text("输入邮箱", "test@example.com")
        
        # 高级操作
        self.aw.login("test@example.com", "password")
    """
    
    def __init__(self, instance_id: int):
        """
        初始化AW Helper
        
        Args:
            instance_id: MuMu模拟器实例ID (0, 1, 2...)
        """
        super().__init__(instance_id)
        logger.debug(f"AWHelper 初始化完成，实例ID: {instance_id}")
    
    def __repr__(self):
        return f"AWHelper(instance_id={self.instance_id})"
