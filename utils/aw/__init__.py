"""
AW (Action Wrapper) 模块
提供分层的UI自动化操作方法

分层结构:
- aw_base.py: 低级AW - 基础ADB操作 (tap, input, press_key等)
- aw_action.py: 中级AW - 组合操作 (click_text, click_image, input_text等)  
- aw_business.py: 高级AW - 业务流程 (login, send_message, create_team等)

使用方式:
    from utils.aw import AWHelper
    
    # 在用户类中
    user.aw = AWHelper(user.device.device_port)
    user.aw.click_text("登录")
    user.aw.input_text("输入邮箱", "test@example.com")
"""

from utils.aw.aw_helper import AWHelper

__all__ = ['AWHelper']
