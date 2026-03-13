"""
轻量级导航器 - 基于JSON配置的路径导航
"""
import json
import subprocess
import time
from typing import List, Dict, Optional
from pathlib import Path


class Navigator:
    """基于配置的导航器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "nav_paths.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.device = self.config["device"]["serial"]
        self.adb = r"D:\MuMuPlayer\nx_main\adb.exe"
        self.paths = self.config["paths"]
        self.elements = self.config["elements"]
    
    def _run_adb(self, *args) -> bool:
        """执行ADB命令"""
        cmd = [self.adb, "-s", self.device] + list(args)
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
        except:
            return False
    
    def tap(self, x: int, y: int) -> bool:
        """点击"""
        return self._run_adb("shell", "input", "tap", str(x), str(y))
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """滑动"""
        return self._run_adb("shell", "input", "swipe", 
                            str(x1), str(y1), str(x2), str(y2), str(duration))
    
    def keyevent(self, key: int) -> bool:
        """按键"""
        return self._run_adb("shell", "input", "keyevent", str(key))
    
    def back(self) -> bool:
        """返回键"""
        return self.keyevent(4)
    
    def execute_step(self, step: Dict) -> bool:
        """执行单个步骤"""
        wait_time = step.get("wait", 1)
        
        if "tap" in step:
            x, y = step["tap"]
            result = self.tap(x, y)
        elif "swipe" in step:
            coords = step["swipe"]
            result = self.swipe(*coords)
        elif "keyevent" in step:
            result = self.keyevent(step["keyevent"])
        else:
            result = True
        
        time.sleep(wait_time)
        return result
    
    def navigate_to(self, target: str, verbose: bool = True) -> bool:
        """
        导航到目标
        
        Args:
            target: 目标名称（如"退出登录"、"创建群组"）
            verbose: 是否打印过程
            
        Returns:
            是否成功
        """
        if target not in self.paths:
            if verbose:
                print(f"[ERROR] 未知目标: {target}")
                print(f"可用目标: {list(self.paths.keys())}")
            return False
        
        steps = self.paths[target]
        
        if verbose:
            print(f"\n导航到: {target}")
            print("-" * 40)
        
        for i, step in enumerate(steps, 1):
            desc = step.get("desc", "")
            if verbose:
                print(f"  步骤{i}: {desc}")
            
            if not self.execute_step(step):
                if verbose:
                    print(f"  [FAIL] 步骤{i}执行失败")
                return False
        
        if verbose:
            print(f"[OK] 已到达: {target}\n")
        
        return True
    
    def get_path(self, target: str) -> Optional[List[Dict]]:
        """获取到目标的路径"""
        return self.paths.get(target)
    
    def list_targets(self) -> List[str]:
        """列出所有可用目标"""
        return list(self.paths.keys())
    
    def click_element(self, element_name: str) -> bool:
        """点击预定义元素"""
        if element_name not in self.elements:
            return False
        
        elem = self.elements[element_name]
        if "tap" in elem:
            return self.tap(*elem["tap"])
        elif "keyevent" in elem:
            return self.keyevent(elem["keyevent"])
        return False


class TestCaseGenerator:
    """测试用例生成器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "nav_paths.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.paths = self.config["paths"]
    
    def generate_navigation_test(self, target: str) -> str:
        """生成单个导航测试用例"""
        if target not in self.paths:
            return f"# 未找到目标: {target}"
        
        steps = self.paths[target]
        safe_name = target.replace(" ", "_").replace("-", "_")
        
        code = f'''"""
测试用例: 导航到{target}
"""
import pytest


class Test{safe_name}:
    """导航到{target}的测试"""

    @pytest.fixture(autouse=True)
    def setup(self, users):
        """测试前初始化"""
        self.userA = users("userA")
        self.userA.login()

    def test_navigate_to_{safe_name}(self):
        """
        测试场景: 导航到{target}
        
        步骤:
'''
        for i, step in enumerate(steps, 1):
            desc = step.get("desc", "执行操作")
            code += f"        {i}. {desc}\n"
        
        code += f'''        
        预期结果: 成功到达{target}
        """
        from utils.navigator import Navigator
        
        nav = Navigator()
        
        # 执行导航
        result = nav.navigate_to("{target}")
        
        # 验证结果
        assert result, "导航到{target}失败"

    def teardown(self):
        """测试后清理"""
        if hasattr(self, 'userA') and self.userA.is_logged_in:
            self.userA.logout()
'''
        return code
    
    def generate_path_test(self, path_name: str, steps: List[Dict]) -> str:
        """根据路径生成测试代码片段"""
        code_lines = []
        for i, step in enumerate(steps, 1):
            desc = step.get("desc", "")
            wait = step.get("wait", 1)
            
            if "tap" in step:
                x, y = step["tap"]
                code_lines.append(f"        # 步骤{i}: {desc}")
                code_lines.append(f"        self.userA.device.tap({x}, {y})")
                code_lines.append(f"        time.sleep({wait})")
            elif "swipe" in step:
                coords = step["swipe"]
                code_lines.append(f"        # 步骤{i}: {desc}")
                code_lines.append(f"        self.userA.device.swipe({coords[0]}, {coords[1]}, {coords[2]}, {coords[3]})")
                code_lines.append(f"        time.sleep({wait})")
            elif "keyevent" in step:
                code_lines.append(f"        # 步骤{i}: {desc}")
                code_lines.append(f"        self.userA.device.keyevent({step['keyevent']})")
                code_lines.append(f"        time.sleep({wait})")
        
        return "\n".join(code_lines)
    
    def generate_smoke_tests(self, output_dir: str = "tests/smoke"):
        """生成冒烟测试套件（验证所有主要路径）"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 选择关键路径进行冒烟测试
        key_targets = [
            "日历页面", "通讯录页面", "设置页面", 
            "搜索页面", "聊天详情页"
        ]
        
        for target in key_targets:
            if target in self.paths:
                code = self.generate_navigation_test(target)
                safe_name = target.replace(" ", "_").replace("-", "_")
                filepath = os.path.join(output_dir, f"test_nav_{safe_name}.py")
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                print(f"[OK] 生成: {filepath}")
        
        print(f"\n共生成 {len(key_targets)} 个冒烟测试用例")
    
    def generate_business_flow_test(self, flow_name: str, targets: List[str]) -> str:
        """
        生成业务流程测试（组合多个导航目标）
        
        Args:
            flow_name: 流程名称
            targets: 目标序列
        """
        safe_name = flow_name.replace(" ", "_").replace("-", "_")
        
        code = f'''"""
测试用例: {flow_name}
业务流程测试 - 组合多个导航步骤
"""
import pytest
import time


class Test{safe_name}:
    """{flow_name}测试"""

    @pytest.fixture(autouse=True)
    def setup(self, users):
        """测试前初始化"""
        self.userA = users("userA")
        self.userA.login()

    def test_{safe_name}(self):
        """
        测试场景: {flow_name}
        
        流程步骤:
'''
        for i, target in enumerate(targets, 1):
            code += f"        {i}. 导航到 {target}\n"
        
        code += f'''        
        预期结果: 完成整个业务流程
        """
        from utils.navigator import Navigator
        
        nav = Navigator()
        
'''
        for i, target in enumerate(targets, 1):
            code += f'''        # 步骤{i}: 导航到 {target}
        assert nav.navigate_to("{target}"), "导航到{target}失败"
        
        # 返回消息页面（准备下一步）
        nav.back()
        time.sleep(1)
        
'''
        
        code += '''        print("业务流程测试完成")

    def teardown(self):
        """测试后清理"""
        if hasattr(self, 'userA') and self.userA.is_logged_in:
            self.userA.logout()
'''
        return code


# ========== 便捷函数 ==========

def nav_to(target: str):
    """快速导航到目标"""
    nav = Navigator()
    return nav.navigate_to(target)


def list_targets():
    """列出所有可用目标"""
    nav = Navigator()
    targets = nav.list_targets()
    print("\n可用的导航目标:")
    print("-" * 40)
    for i, t in enumerate(targets, 1):
        print(f"  {i}. {t}")
    print(f"\n共 {len(targets)} 个目标")
    return targets


def generate_test(target: str, save_path: str = None):
    """生成测试用例"""
    gen = TestCaseGenerator()
    code = gen.generate_navigation_test(target)
    
    if save_path:
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"测试用例已保存到: {save_path}")
    else:
        print(code)
    
    return code


# ========== 主程序演示 ==========

if __name__ == "__main__":
    print("=" * 60)
    print("POPO导航器演示")
    print("=" * 60)
    
    # 列出所有目标
    list_targets()
    
    # 生成测试用例示例
    print("\n" + "=" * 60)
    print("生成测试用例示例: 退出登录")
    print("=" * 60)
    generate_test("退出登录")
