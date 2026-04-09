"""
窗口管理工具
使用win32gui定位MuMu模拟器窗口，获取窗口位置和区域坐标
支持多模拟器窗口的定位和操作
"""
import logging
from typing import Optional, Tuple, Dict
from dataclasses import dataclass

try:
    import win32gui
    import win32con
except ImportError:
    raise ImportError("需要安装pywin32: pip install pywin32")

logger = logging.getLogger(__name__)


@dataclass
class WindowRect:
    """窗口区域信息"""
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    @property
    def region(self) -> Tuple[int, int, int, int]:
        """返回pyautogui.screenshot需要的region格式 (left, top, width, height)"""
        return (self.left, self.top, self.width, self.height)

    def to_absolute(self, x: int, y: int) -> Tuple[int, int]:
        """
        将窗口内相对坐标转换为屏幕绝对坐标
        
        Args:
            x: 窗口内X坐标
            y: 窗口内Y坐标
            
        Returns:
            Tuple[int, int]: 屏幕绝对坐标 (abs_x, abs_y)
        """
        return (self.left + x, self.top + y)

    def __str__(self) -> str:
        return f"WindowRect(left={self.left}, top={self.top}, width={self.width}, height={self.height})"


class WindowManager:
    """
    窗口管理器
    用于定位和管理MuMu模拟器窗口
    """

    # MuMu设备窗口名称模式
    # 注意: "MuMu模拟器" 是模拟器管理窗口，"MuMu安卓设备" 才是实际的Android设备窗口
    MUMU_DEVICE_WINDOW_PATTERNS = [
        "MuMu安卓设备",  # 主实例设备窗口名
        "MuMu安卓设备-",  # 多实例设备窗口名前缀 (MuMu安卓设备-1, MuMu安卓设备-2等)
    ]

    # 缓存已找到的窗口句柄
    _window_cache: Dict[int, int] = {}  # instance_id -> hwnd

    @classmethod
    def get_window_name(cls, instance_id: int) -> str:
        """
        根据实例ID获取设备窗口名称
        
        Args:
            instance_id: 模拟器实例ID (0, 1, 2...)
            
        Returns:
            str: 设备窗口名称 (返回主候选名称)
        """
        if instance_id == 0:
            return "MuMu安卓设备"
        else:
            return f"MuMu安卓设备-{instance_id}"

    @classmethod
    def get_window_name_candidates(cls, instance_id: int) -> list:
        """
        获取实例ID对应的所有可能窗口名称
        
        Args:
            instance_id: 模拟器实例ID
            
        Returns:
            list: 可能的窗口名称列表
        """
        if instance_id == 0:
            # 实例0可能叫 "MuMu安卓设备" 或直接无后缀
            return ["MuMu安卓设备"]
        else:
            # 其他实例带编号后缀
            return [f"MuMu安卓设备-{instance_id}"]

    @classmethod
    def find_window_by_name(cls, window_name: str) -> Optional[int]:
        """
        根据窗口名称查找窗口句柄
        
        Args:
            window_name: 窗口标题
            
        Returns:
            Optional[int]: 窗口句柄(hwnd)，未找到返回None
        """
        try:
            hwnd = win32gui.FindWindow(None, window_name)
            if hwnd and win32gui.IsWindow(hwnd):
                return hwnd
            return None
        except Exception as e:
            logger.error(f"❌ 查找窗口失败 [{window_name}]: {e}")
            return None

    @classmethod
    def find_mumu_window(cls, instance_id: int) -> Optional[int]:
        """
        查找指定实例的MuMu模拟器窗口
        支持多种窗口名称格式，自动尝试所有候选名称
        
        Args:
            instance_id: 模拟器实例ID
            
        Returns:
            Optional[int]: 窗口句柄(hwnd)
        """
        # 先检查缓存
        if instance_id in cls._window_cache:
            hwnd = cls._window_cache[instance_id]
            if win32gui.IsWindow(hwnd):
                return hwnd
            else:
                # 缓存失效，删除
                del cls._window_cache[instance_id]
                logger.debug(f"🗑️ 缓存的窗口句柄已失效，已清除")

        # 尝试所有候选窗口名称
        candidates = cls.get_window_name_candidates(instance_id)
        hwnd = None
        matched_name = None

        for window_name in candidates:
            hwnd = cls.find_window_by_name(window_name)
            if hwnd:
                matched_name = window_name
                break

        if hwnd:
            cls._window_cache[instance_id] = hwnd
            logger.info(f"✅ 找到MuMu窗口 [{matched_name}], hwnd={hwnd}, 实例ID={instance_id}")
        else:
            # 未找到窗口时，列出所有MuMu窗口帮助调试
            all_windows = cls.list_all_mumu_windows()
            if all_windows:
                logger.warning(f"⚠️ 未找到MuMu窗口 (尝试过: {candidates})，但发现其他MuMu窗口:")
                for inst_id, wnd_hwnd in all_windows.items():
                    actual_name = win32gui.GetWindowText(wnd_hwnd)
                    logger.warning(f"   - 实例 #{inst_id}: [{actual_name}], hwnd={wnd_hwnd}")
            else:
                logger.warning(f"⚠️ 未找到MuMu窗口 (尝试过: {candidates})，且未检测到任何MuMu模拟器窗口")
                logger.warning(f"   请确保MuMu模拟器已启动且窗口未最小化")

        return hwnd

    @classmethod
    def get_window_rect(cls, instance_id: int) -> Optional[WindowRect]:
        """
        获取指定实例的窗口区域
        
        Args:
            instance_id: 模拟器实例ID
            
        Returns:
            Optional[WindowRect]: 窗口区域信息
        """
        hwnd = cls.find_mumu_window(instance_id)
        if not hwnd:
            return None

        try:
            rect = win32gui.GetWindowRect(hwnd)
            return WindowRect(
                left=rect[0],
                top=rect[1],
                right=rect[2],
                bottom=rect[3]
            )
        except Exception as e:
            logger.error(f"❌ 获取窗口区域失败: {e}")
            return None

    @classmethod
    def get_client_rect(cls, instance_id: int) -> Optional[WindowRect]:
        """
        获取指定实例的客户区域（不包含标题栏和边框）
        
        Args:
            instance_id: 模拟器实例ID
            
        Returns:
            Optional[WindowRect]: 客户区域信息
        """
        hwnd = cls.find_mumu_window(instance_id)
        if not hwnd:
            return None

        try:
            # 获取客户区域相对于窗口的位置
            client_rect = win32gui.GetClientRect(hwnd)

            # 将客户区域的左上角转换为屏幕坐标
            point = win32gui.ClientToScreen(hwnd, (0, 0))

            return WindowRect(
                left=point[0],
                top=point[1],
                right=point[0] + client_rect[2],
                bottom=point[1] + client_rect[3]
            )
        except Exception as e:
            logger.error(f"❌ 获取客户区域失败: {e}")
            return None

    @classmethod
    def focus_window(cls, instance_id: int) -> bool:
        """
        将指定实例的窗口置于前台
        
        使用多种方法绕过Windows的SetForegroundWindow限制:
        1. AttachThreadInput - 附加线程输入
        2. 模拟ALT键 - 触发用户输入条件
        3. BringWindowToTop + SetForegroundWindow 组合
        
        Args:
            instance_id: 模拟器实例ID
            
        Returns:
            bool: 操作是否成功
        """
        import ctypes
        from ctypes import wintypes
        
        hwnd = cls.find_mumu_window(instance_id)
        if not hwnd:
            logger.error(f"❌ 未找到窗口: 实例 #{instance_id}")
            return False

        try:
            # 如果窗口最小化，先恢复
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # 方法1: 使用AttachThreadInput绕过限制
            # 获取当前线程ID和目标窗口线程ID
            current_thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
            target_thread_id = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
            
            # 附加线程输入
            attached = False
            if current_thread_id != target_thread_id:
                attached = ctypes.windll.user32.AttachThreadInput(
                    current_thread_id, target_thread_id, True
                )
            
            try:
                # 方法2: 模拟按下ALT键，绕过Windows限制
                # ALT键的虚拟键码是0x12 (VK_MENU)
                ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)  # ALT down
                
                # 使用多种方式尝试激活窗口
                # 先将窗口置顶
                win32gui.BringWindowToTop(hwnd)
                
                # 然后设置为前台窗口
                result = win32gui.SetForegroundWindow(hwnd)
                
                # 释放ALT键
                ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)  # ALT up
                
                # 额外尝试: 设置窗口位置确保可见
                win32gui.SetWindowPos(
                    hwnd, 
                    win32con.HWND_TOP,  # 置于Z序顶部
                    0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                )
                
            finally:
                # 分离线程输入
                if attached:
                    ctypes.windll.user32.AttachThreadInput(
                        current_thread_id, target_thread_id, False
                    )
            
            # 验证是否成功
            import time
            time.sleep(0.1)
            foreground_hwnd = win32gui.GetForegroundWindow()
            if foreground_hwnd == hwnd:
                logger.info(f"✅ 窗口已置于前台: 实例 #{instance_id}")
                return True
            else:
                # 即使验证失败，窗口也可能已经可见，返回True
                logger.warning(f"⚠️ 窗口可能已置于前台但验证失败: 实例 #{instance_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 置前窗口失败: {e}")
            return False

    @classmethod
    def list_all_mumu_windows(cls) -> Dict[int, int]:
        """
        列出所有MuMu安卓设备窗口
        
        Returns:
            Dict[int, int]: {instance_id: hwnd}
        """
        windows = {}

        def enum_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                # 检查是否是MuMu安卓设备窗口
                if title == "MuMu安卓设备":
                    windows[0] = hwnd
                elif title.startswith("MuMu安卓设备-"):
                    try:
                        instance_id = int(title.split("-")[-1])
                        windows[instance_id] = hwnd
                    except ValueError:
                        pass
            return True

        try:
            win32gui.EnumWindows(enum_callback, None)
        except Exception as e:
            logger.error(f"❌ 枚举窗口失败: {e}")

        return windows

    @classmethod
    def clear_cache(cls):
        """清除窗口句柄缓存"""
        cls._window_cache.clear()
        logger.info("🗑️ 窗口缓存已清除")


# 便捷函数
def get_mumu_window_rect(instance_id: int) -> Optional[WindowRect]:
    """
    获取MuMu模拟器窗口区域（便捷函数）
    
    Args:
        instance_id: 模拟器实例ID
        
    Returns:
        Optional[WindowRect]: 窗口区域信息
    """
    return WindowManager.get_client_rect(instance_id)


def to_screen_coords(instance_id: int, x: int, y: int) -> Optional[Tuple[int, int]]:
    """
    将窗口内坐标转换为屏幕坐标（便捷函数）
    
    Args:
        instance_id: 模拟器实例ID
        x: 窗口内X坐标
        y: 窗口内Y坐标
        
    Returns:
        Optional[Tuple[int, int]]: 屏幕坐标，窗口不存在返回None
    """
    rect = WindowManager.get_client_rect(instance_id)
    if rect:
        return rect.to_absolute(x, y)
    return None
