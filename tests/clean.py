
import subprocess
import sys

def cleanup_packages():
    # 获取已安装的包列表
    installed_packages = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--format=freeze']).decode('utf-8')
    package_list = [pkg.split('==')[0] for pkg in installed_packages.split('\n') if pkg and '==' in pkg]

    # 卸载所有包
    for package in package_list:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', package, '-y'])
            print(f"已卸载: {package}")
        except subprocess.CalledProcessError as e:
            print(f"卸载失败: {package}, 错误: {e}")

if __name__ == "__main__":
    cleanup_packages()