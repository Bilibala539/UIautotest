"""
初始化虚拟设备
每次启动虚拟设备，会重装网易POPO

改变【配置区】的DOWNLOAD_URL可以换安装包

"""

import subprocess
import time
import os
import tempfile
import urllib.request
from dataclasses import dataclass
from typing import List, Optional
from utils.window_manager import WindowManager

# ==================【配置区】==================
MUMU_INSTALL_PATH = r"C:\Program Files\Netease\MuMu\nx_main"  # MuMu12安装目录
DOWNLOAD_URL = r"https://popo.netease.com/file/popoandroid/popo_origin-release_4.21.0_prod_1774944232398.apk"  # 包体的下载链接

DEVICE_COUNT = 1  # 启动设备数量（1-3）
LAUNCH_WAIT = 25  # 启动等待时间（秒）
MAX_DEVICES = 3  # 最大设备数
CLOSE_WAIT = 3  # 关闭模拟器后等待时间（秒）

# 窗口配置
WINDOW_WIDTH = 540  # 窗口宽度
WINDOW_HEIGHT = 960  # 窗口高度
WINDOW_GAP = 0  # 窗口间距


@dataclass
class Device:
    """虚拟设备类"""

    def __init__(self, instance_id, window_name, window_x, window_y,
                 window_width, window_height,
                 adb_address, adb_port, is_ready):
        self.pos = (window_x, window_y)
        self.size = (window_width, window_height)

        self.instance_id = instance_id
        self.window_name = window_name
        self.adb_address = adb_address
        self.adb_port = adb_port
        self.is_ready = is_ready

    def __str__(self) -> str:
        return f"Device(#{self.instance_id}, {self.window_name}, {self.adb_address})"

    def __repr__(self) -> str:
        return self.__str__()


def is_mumu_running() -> bool:
    """检测MuMu模拟器是否正在运行"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq MuMuPlayer.exe"],
            capture_output=True, text=True, timeout=10
        )
        if "MuMuPlayer.exe" in result.stdout:
            return True

        # 也检查 MuMuVMMHeadless.exe（后台进程）
        result2 = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq MuMuVMMHeadless.exe"],
            capture_output=True, text=True, timeout=10
        )
        return "MuMuVMMHeadless.exe" in result2.stdout
    except:
        return False


def close_all_mumu() -> bool:
    """使用MuMuManager.exe API关闭所有虚拟设备"""
    manager_path = os.path.join(MUMU_INSTALL_PATH, "MuMuManager.exe")

    if not os.path.exists(manager_path):
        return False

    # 关闭所有实例 (0到MAX_DEVICES-1)
    for i in range(MAX_DEVICES):
        # 命令格式: MuMuManager.exe api -v <id> shutdown_player
        cmd = [manager_path, "api", "-v", str(i), "shutdown_player"]
        subprocess.run(cmd, capture_output=True, timeout=10)
    return True


def get_adb_port(instance_id: int) -> int:
    """获取MuMu12实例的ADB端口: 16384 + (instance_id * 32)"""
    return 16384 + (instance_id * 32)

# 别名函数，兼容aw_business.py的导入
def get_device_port_by_instance(instance_id: int) -> int:
    """获取MuMu12实例的ADB端口（get_adb_port的别名）"""
    return get_adb_port(instance_id)

def get_player_path() -> str:
    """获取MuMu模拟器程序路径"""
    for name in ["MuMuPlayer.exe", "MuMuNxMain.exe"]:
        path = os.path.join(MUMU_INSTALL_PATH, name)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"找不到MuMu程序: {MUMU_INSTALL_PATH}")


def get_adb() -> str:
    """获取ADB路径"""
    paths = [
        os.path.join(os.path.dirname(MUMU_INSTALL_PATH), "vmonitor", "bin", "adb_server.exe"),
        os.path.join(MUMU_INSTALL_PATH, "adb.exe")
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return "adb"


# ADB路径常量（供其他模块导入使用）
ADB_PATH = get_adb()


# ==================【APK安装功能】==================
POPO_PACKAGE = "com.netease.popo"  # 网易POPO包名


def check_app_installed(port: int, package_name: str) -> bool:
    """
    检查设备上是否已安装指定应用
    
    Args:
        port: 设备ADB端口
        package_name: 应用包名
        
    Returns:
        bool: 是否已安装
    """
    device_serial = f"127.0.0.1:{port}"
    try:
        result = subprocess.run(
            [get_adb(), "-s", device_serial, "shell", "pm", "list", "packages", package_name],
            capture_output=True, text=True, timeout=10
        )
        return f"package:{package_name}" in result.stdout
    except Exception as e:
        print(f"   [WARN] 检查应用安装状态失败: {e}")
        return False


def uninstall_app(port: int, package_name: str, timeout: int = 30) -> bool:
    """
    卸载设备上的指定应用
    
    Args:
        port: 设备ADB端口
        package_name: 应用包名
        timeout: 卸载超时时间（秒）
        
    Returns:
        bool: 卸载是否成功
    """
    device_serial = f"127.0.0.1:{port}"
    try:
        print(f"   [DEL] 正在卸载 {package_name}...")
        result = subprocess.run(
            [get_adb(), "-s", device_serial, "uninstall", package_name],
            capture_output=True, text=True, timeout=timeout
        )

        if "Success" in result.stdout:
            print(f"   [OK] 卸载成功")
            return True
        else:
            error_msg = result.stdout.strip() or result.stderr.strip()
            print(f"   [FAIL] 卸载失败: {error_msg}")
            return False
    except subprocess.TimeoutExpired:
        print(f"   [FAIL] 卸载超时")
        return False
    except Exception as e:
        print(f"   [FAIL] 卸载异常: {e}")
        return False


def download_apk(url: str, save_path: Optional[str] = None) -> Optional[str]:
    """
    下载APK文件
    
    Args:
        url: APK下载链接
        save_path: 保存路径，如果为None则保存到临时目录
        
    Returns:
        Optional[str]: 下载后的文件路径，失败返回None
    """
    try:
        if save_path is None:
            # 从URL中提取文件名
            filename = url.split("/")[-1]
            if not filename.endswith(".apk"):
                filename = "downloaded_app.apk"
            save_path = os.path.join(tempfile.gettempdir(), filename)

        print(f"[DOWNLOAD] 正在下载APK: {url}")
        print(f"   保存到: {save_path}")

        urllib.request.urlretrieve(url, save_path)

        if os.path.exists(save_path):
            file_size = os.path.getsize(save_path) / (1024 * 1024)  # MB
            print(f"   [OK] 下载完成 ({file_size:.2f} MB)")
            return save_path
        else:
            print("   [FAIL] 下载失败：文件不存在")
            return None
    except Exception as e:
        print(f"   [FAIL] 下载失败: {e}")
        return None


def install_apk_to_device(apk_path: str, port: int, timeout: int = 120) -> bool:
    """
    安装APK到指定设备
    
    Args:
        apk_path: APK文件路径
        port: 设备ADB端口
        timeout: 安装超时时间（秒）
        
    Returns:
        bool: 安装是否成功
    """
    if not os.path.exists(apk_path):
        print(f"   [FAIL] APK文件不存在: {apk_path}")
        return False

    device_serial = f"127.0.0.1:{port}"
    try:
        print(f"   [INSTALL] 正在安装到 {device_serial}...")
        result = subprocess.run(
            [get_adb(), "-s", device_serial, "install", "-r", "-d", apk_path],
            capture_output=True, text=True, timeout=timeout
        )

        if "Success" in result.stdout:
            print(f"   [OK] 安装成功")
            return True
        else:
            error_msg = result.stdout.strip() or result.stderr.strip()
            print(f"   [FAIL] 安装失败: {error_msg}")
            return False
    except subprocess.TimeoutExpired:
        print(f"   [FAIL] 安装超时")
        return False
    except Exception as e:
        print(f"   [FAIL] 安装异常: {e}")
        return False


def install_apk_to_all_devices(devices: List['Device'], apk_path: Optional[str] = None) -> int:
    """
    安装APK到所有已就绪的设备
    安装前会检查设备是否已安装网易POPO，如果已安装则先卸载
    
    Args:
        devices: Device对象列表
        apk_path: APK文件路径，如果为None则从DOWNLOAD_URL下载
        
    Returns:
        int: 成功安装的设备数量
    """
    ready_devices = [d for d in devices if d.is_ready]

    if not ready_devices:
        print("[WARN] 没有就绪的设备可以安装APK")
        return 0

    print(f"\n[INFO] 开始在 {len(ready_devices)} 台设备上安装APK...")

    # 第一步：检查并卸载已安装的POPO应用
    print(f"\n[CHECK] 检查设备上是否已安装网易POPO ({POPO_PACKAGE})...")
    for device in ready_devices:
        print(f"\n设备 #{device.instance_id} ({device.adb_address}):")
        if check_app_installed(device.adb_port, POPO_PACKAGE):
            print(f"   [WARN] 检测到已安装网易POPO，需要先卸载")
            uninstall_app(device.adb_port, POPO_PACKAGE)
        else:
            print(f"   [OK] 未安装网易POPO，无需卸载")

    # 第二步：下载APK（如果没有提供APK路径）
    if apk_path is None:
        print(f"\n")
        apk_path = download_apk(DOWNLOAD_URL)
        if apk_path is None:
            print("[ERROR] APK下载失败，无法安装")
            return 0

    # 第三步：安装APK到所有设备
    success_count = 0
    print(f"\n[INSTALL] 开始安装APK到 {len(ready_devices)} 台设备...")

    for device in ready_devices:
        print(f"\n设备 #{device.instance_id} ({device.adb_address}):")
        if install_apk_to_device(apk_path, device.adb_port):
            success_count += 1

    print(f"\n[DONE] APK安装完成: {success_count}/{len(ready_devices)} 台设备成功")
    return success_count


def start_emulator(instance_id: int) -> bool:
    """启动模拟器实例"""
    try:
        subprocess.Popen(
            [get_player_path(), "-v", str(instance_id)],
            cwd=MUMU_INSTALL_PATH,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except:
        return False


def adb_connect(port: int) -> bool:
    """连接ADB"""
    try:
        result = subprocess.run(
            [get_adb(), "connect", f"127.0.0.1:{port}"],
            capture_output=True, text=True, timeout=10
        )
        return "connected" in result.stdout.lower()
    except:
        return False


def wait_device_ready(port: int, timeout: int = 60) -> bool:
    """等待设备就绪"""
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            result = subprocess.run(
                [get_adb(), "-s", f"127.0.0.1:{port}", "shell", "getprop", "sys.boot_completed"],
                capture_output=True, text=True, timeout=5
            )
            if result.stdout.strip() == "1":
                return True
        except:
            pass
        time.sleep(2)
    return False


def set_window_size_and_arrange(count: int) -> bool:
    """
    设置模拟器窗口大小为540x960并排列窗口
    """
    for i in range(count):
        # 计算窗口位置（横向排列）
        x = WINDOW_GAP + i * (WINDOW_WIDTH + WINDOW_GAP)
        y = WINDOW_GAP

        # 使用MuMuManager设置窗口大小和位置
        # 命令格式: MuMuManager.exe api -v <id> set_window_size -w <width> -h <height>
        manager_exe = os.path.join(MUMU_INSTALL_PATH, "MuMuManager.exe")
        cmd_pos = f'"{manager_exe}" control -v {str(i)} layout_window -sw {str(WINDOW_WIDTH)} -sh {str(WINDOW_HEIGHT)}'
        subprocess.run(cmd_pos, capture_output=True, timeout=5, shell=True)

        # 设置窗口位置
        # 命令格式: MuMuManager.exe api -v <id> set_window_pos -x <x> -y <y>
        cmd_pos = f'"{manager_exe}" control -v {str(i)} layout_window -px {str(x)} -py {str(y)}'
        subprocess.run(cmd_pos, capture_output=True, timeout=5)

    return True


def get_window_name(instance_id: int) -> str:
    """获取窗口名称"""
    if instance_id == 0:
        return "MuMu模拟器12"
    else:
        return f"MuMu模拟器12-{instance_id}"


def start_devices(count: int = DEVICE_COUNT) -> List[Device]:
    """
    启动多台虚拟设备并排列窗口

    Args:
        count: 启动数量（1-3）

    Returns:
        List[Device]: Device对象列表
    """
    count = min(max(1, count), MAX_DEVICES)
    devices: List[Device] = []

    # 检测并关闭已运行的模拟器
    if is_mumu_running():
        print("检测到MuMu模拟器正在运行，正在关闭...")
        close_all_mumu()
        time.sleep(CLOSE_WAIT)
        print("  [OK] 已关闭")

    print(f"启动 {count} 台虚拟设备...")

    # 启动所有实例
    for i in range(count):
        if start_emulator(i):
            print(f"  实例 #{i} 启动中...")
        time.sleep(2)

    # 等待启动
    print(f"等待启动 ({LAUNCH_WAIT}秒)...")
    time.sleep(LAUNCH_WAIT)

    # 连接ADB并创建Device对象
    for i in range(count):
        port = get_adb_port(i)
        addr = f"127.0.0.1:{port}"

        # 计算窗口位置（横向排列）
        window_x = WINDOW_GAP + i * (WINDOW_WIDTH + WINDOW_GAP)
        window_y = WINDOW_GAP

        # 获取窗口名称
        window_name = get_window_name(i)

        # 连接ADB并检测设备状态
        is_ready = False
        if adb_connect(port):
            if wait_device_ready(port, timeout=30):
                is_ready = True
                print(f"  [OK] {addr} 就绪")
            else:
                print(f"  [WARN] {addr} 未完全就绪")
        else:
            print(f"  [FAIL] {addr} 连接失败")

        # 创建Device对象
        device = Device(
            instance_id=i,
            window_name=window_name,
            window_x=window_x,
            window_y=window_y,
            window_width=WINDOW_WIDTH,
            window_height=WINDOW_HEIGHT,
            adb_address=addr,
            adb_port=port,
            is_ready=is_ready
        )
        devices.append(device)

    # 设置窗口大小并排列
    print(f"设置窗口大小 {WINDOW_WIDTH}x{WINDOW_HEIGHT} 并排列...")
    set_window_size_and_arrange(count)

    ready_count = sum(1 for d in devices if d.is_ready)
    print(f"完成: {ready_count}/{count} 台设备就绪")

    # 安装APK到所有设备
    install_apk_to_all_devices(devices)

    # 激活所有设备窗口至前台（获得焦点）
    print("[WIN] 激活设备窗口至前台...")
    for device in devices:
        WindowManager.focus_window(device.instance_id)
    
    # 激活第一个窗口（确保有焦点）
    if devices:
        WindowManager.focus_window(devices[0].instance_id)

    return devices


# def main():
#     """主函数"""
#     devices = start_devices(DEVICE_COUNT)
#     for device in devices:
#         print(f"device.instance_id:{device.instance_id}")
#         print(f"device.window_name:{device.window_name}")
#         print(f"device.pos:({device.pos})")
#         print(f"device.size:({device.size})")
#         print(f"device.adb_address:{device.adb_address}")
#         print(f"device.adb_port:{device.adb_port}")
#
#
# if __name__ == "__main__":
#     main()
