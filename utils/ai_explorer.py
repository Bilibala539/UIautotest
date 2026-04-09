"""
AI自主探索器 - 自动探索网易POPO应用
通过截图分析、点击操作、变化检测来学习UI交互逻辑
"""

import os
import json
import time
import subprocess
from datetime import datetime
from typing import Optional, Tuple, List, Dict
from PIL import Image
import io
import hashlib

from utils.devices import get_adb, POPO_PACKAGE


class AIExplorer:
    """AI自主探索器"""
    
    def __init__(self, device_port: int, output_dir: str = "explorer_output"):
        """
        初始化探索器
        
        Args:
            device_port: 设备ADB端口
            output_dir: 探索结果输出目录
        """
        self.device_port = device_port
        self.device_serial = f"127.0.0.1:{device_port}"
        self.adb = get_adb()
        self.output_dir = output_dir
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "screenshots"), exist_ok=True)
        
        # 探索记录
        self.exploration_log: List[Dict] = []
        self.page_signatures: Dict[str, str] = {}  # 页面签名 -> 页面名称
        self.action_mappings: List[Dict] = []  # 操作与结果映射
        
        # 探索计数
        self.step_count = 0
    
    def _run_adb(self, *args) -> subprocess.CompletedProcess:
        """执行ADB命令"""
        cmd = [self.adb, "-s", self.device_serial] + list(args)
        return subprocess.run(cmd, capture_output=True, timeout=30)
    
    def take_screenshot(self, save_name: Optional[str] = None) -> Optional[Image.Image]:
        """
        截取当前屏幕
        
        Args:
            save_name: 保存文件名（可选）
            
        Returns:
            PIL Image对象
        """
        try:
            result = self._run_adb("exec-out", "screencap", "-p")
            if result.returncode == 0 and result.stdout:
                img = Image.open(io.BytesIO(result.stdout))
                
                if save_name:
                    save_path = os.path.join(self.output_dir, "screenshots", save_name)
                    img.save(save_path)
                    
                return img
        except Exception as e:
            print(f"[ERROR] 截图失败: {e}")
        return None
    
    def get_page_signature(self, img: Image.Image) -> str:
        """
        生成页面签名（用于识别相同页面）
        使用图片哈希来标识页面
        """
        # 缩小图片并转为灰度，生成简单签名
        small = img.resize((32, 32)).convert('L')
        pixels = list(small.getdata())
        avg = sum(pixels) / len(pixels)
        bits = ''.join('1' if p > avg else '0' for p in pixels)
        return hashlib.md5(bits.encode()).hexdigest()[:16]
    
    def tap(self, x: int, y: int) -> bool:
        """
        点击指定坐标
        
        Args:
            x: X坐标
            y: Y坐标
            
        Returns:
            是否成功
        """
        try:
            result = self._run_adb("shell", "input", "tap", str(x), str(y))
            return result.returncode == 0
        except Exception as e:
            print(f"[ERROR] 点击失败: {e}")
            return False
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """滑动操作"""
        try:
            result = self._run_adb("shell", "input", "swipe", 
                                   str(x1), str(y1), str(x2), str(y2), str(duration))
            return result.returncode == 0
        except:
            return False
    
    def press_back(self) -> bool:
        """按返回键"""
        try:
            result = self._run_adb("shell", "input", "keyevent", "4")
            return result.returncode == 0
        except:
            return False
    
    def launch_app(self, package: str = POPO_PACKAGE) -> bool:
        """启动应用"""
        try:
            # 获取启动Activity
            result = self._run_adb("shell", "monkey", "-p", package, 
                                   "-c", "android.intent.category.LAUNCHER", "1")
            time.sleep(3)  # 等待应用启动
            return result.returncode == 0
        except:
            return False
    
    def compare_screenshots(self, img1: Image.Image, img2: Image.Image) -> Dict:
        """
        比较两张截图的差异
        
        Returns:
            包含差异信息的字典
        """
        # 计算签名
        sig1 = self.get_page_signature(img1)
        sig2 = self.get_page_signature(img2)
        
        # 简单的像素差异计算
        if img1.size != img2.size:
            return {"same_page": False, "change_type": "size_changed", "sig1": sig1, "sig2": sig2}
        
        # 转换为相同模式进行比较
        arr1 = list(img1.convert('RGB').getdata())
        arr2 = list(img2.convert('RGB').getdata())
        
        diff_count = sum(1 for p1, p2 in zip(arr1, arr2) if p1 != p2)
        total_pixels = len(arr1)
        diff_ratio = diff_count / total_pixels
        
        return {
            "same_page": sig1 == sig2,
            "diff_ratio": diff_ratio,
            "change_type": "no_change" if diff_ratio < 0.01 else ("minor" if diff_ratio < 0.3 else "major"),
            "sig_before": sig1,
            "sig_after": sig2
        }
    
    def analyze_clickable_regions(self, img: Image.Image) -> List[Dict]:
        """
        分析图片中可能可点击的区域
        基于简单的视觉特征识别（颜色、位置等）
        
        Returns:
            可点击区域列表
        """
        width, height = img.size
        regions = []
        
        # 定义常见的可点击区域
        # 底部导航栏（通常在底部 1/8 区域）
        nav_y = int(height * 0.9)
        nav_height = int(height * 0.1)
        for i in range(5):  # 假设5个导航项
            x = int(width * (i + 0.5) / 5)
            regions.append({
                "name": f"底部导航_{i+1}",
                "x": x,
                "y": nav_y,
                "type": "navigation",
                "priority": 2
            })
        
        # 顶部操作区域
        top_y = int(height * 0.12)
        regions.append({"name": "顶部左侧", "x": int(width * 0.1), "y": top_y, "type": "header", "priority": 3})
        regions.append({"name": "顶部右侧搜索", "x": int(width * 0.8), "y": top_y, "type": "header", "priority": 3})
        regions.append({"name": "顶部右侧添加", "x": int(width * 0.9), "y": top_y, "type": "header", "priority": 3})
        
        # 中间内容区域（列表项）
        for i in range(5):
            y = int(height * (0.3 + i * 0.12))
            regions.append({
                "name": f"列表项_{i+1}",
                "x": int(width * 0.5),
                "y": y,
                "type": "list_item",
                "priority": 1
            })
        
        # 中心区域（可能的弹窗按钮）
        regions.append({"name": "中心区域", "x": int(width * 0.5), "y": int(height * 0.5), "type": "center", "priority": 4})
        
        return regions
    
    def explore_step(self, click_region: Dict) -> Dict:
        """
        执行一步探索
        
        Args:
            click_region: 要点击的区域信息
            
        Returns:
            探索结果
        """
        self.step_count += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 截图（点击前）
        before_img = self.take_screenshot(f"step{self.step_count:03d}_before.png")
        if not before_img:
            return {"success": False, "error": "截图失败"}
        
        before_sig = self.get_page_signature(before_img)
        
        # 2. 执行点击
        x, y = click_region["x"], click_region["y"]
        print(f"[Step {self.step_count}] 点击 {click_region['name']} ({x}, {y})")
        
        click_success = self.tap(x, y)
        time.sleep(1.5)  # 等待页面响应
        
        # 3. 截图（点击后）
        after_img = self.take_screenshot(f"step{self.step_count:03d}_after.png")
        if not after_img:
            return {"success": False, "error": "点击后截图失败"}
        
        # 4. 分析变化
        comparison = self.compare_screenshots(before_img, after_img)
        
        # 5. 记录结果
        result = {
            "step": self.step_count,
            "timestamp": timestamp,
            "action": {
                "type": "tap",
                "target": click_region["name"],
                "x": x,
                "y": y,
                "region_type": click_region.get("type", "unknown")
            },
            "result": {
                "success": click_success,
                "page_changed": not comparison["same_page"],
                "change_type": comparison["change_type"],
                "diff_ratio": comparison.get("diff_ratio", 0),
                "before_signature": before_sig,
                "after_signature": comparison["sig_after"]
            },
            "interpretation": self._interpret_change(comparison, click_region)
        }
        
        self.exploration_log.append(result)
        self.action_mappings.append(result)
        
        return result
    
    def _interpret_change(self, comparison: Dict, click_region: Dict) -> str:
        """解释页面变化的含义"""
        if comparison["change_type"] == "no_change":
            return "点击无响应，可能不是可点击元素或已在当前状态"
        elif comparison["change_type"] == "minor":
            return "页面有轻微变化，可能是状态切换、高亮或小动画"
        elif comparison["change_type"] == "major":
            if click_region.get("type") == "navigation":
                return "页面切换，可能是导航到新页面"
            elif click_region.get("type") == "list_item":
                return "打开了详情页面或对话"
            else:
                return "页面发生重大变化，可能打开了新页面或弹窗"
        return "变化类型未知"
    
    def save_exploration_results(self):
        """保存探索结果"""
        # 保存探索日志
        log_path = os.path.join(self.output_dir, "exploration_log.json")
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.exploration_log, f, ensure_ascii=False, indent=2)
        
        # 保存操作映射
        mapping_path = os.path.join(self.output_dir, "action_mappings.json")
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(self.action_mappings, f, ensure_ascii=False, indent=2)
        
        # 生成摘要报告
        self._generate_summary_report()
        
        print(f"\n[DONE] 探索结果已保存到: {self.output_dir}")
    
    def _generate_summary_report(self):
        """生成探索摘要报告"""
        report_path = os.path.join(self.output_dir, "exploration_report.md")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# POPO应用探索报告\n\n")
            f.write(f"探索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总步骤数: {self.step_count}\n\n")
            
            f.write("## 操作与响应映射\n\n")
            f.write("| 步骤 | 操作目标 | 坐标 | 页面变化 | 解释 |\n")
            f.write("|------|----------|------|----------|------|\n")
            
            for record in self.exploration_log:
                action = record["action"]
                result = record["result"]
                f.write(f"| {record['step']} | {action['target']} | ({action['x']}, {action['y']}) | ")
                f.write(f"{result['change_type']} | {record['interpretation']} |\n")
            
            f.write("\n## 页面签名记录\n\n")
            unique_sigs = set()
            for record in self.exploration_log:
                unique_sigs.add(record["result"]["before_signature"])
                unique_sigs.add(record["result"]["after_signature"])
            f.write(f"发现 {len(unique_sigs)} 个不同的页面状态\n")
    
    def auto_explore(self, max_steps: int = 20) -> List[Dict]:
        """
        自动探索应用
        
        Args:
            max_steps: 最大探索步数
            
        Returns:
            探索记录列表
        """
        print(f"\n{'='*50}")
        print(f"开始自动探索 POPO 应用 (最多 {max_steps} 步)")
        print(f"{'='*50}\n")
        
        # 启动应用
        print("[INFO] 启动 POPO 应用...")
        self.launch_app()
        time.sleep(3)
        
        # 获取初始截图
        init_img = self.take_screenshot("step000_initial.png")
        if init_img:
            init_sig = self.get_page_signature(init_img)
            print(f"[INFO] 初始页面签名: {init_sig}")
        
        # 分析可点击区域
        regions = self.analyze_clickable_regions(init_img)
        
        # 按优先级排序
        regions.sort(key=lambda r: r.get("priority", 99))
        
        # 开始探索
        explored_count = 0
        for region in regions:
            if explored_count >= max_steps:
                break
                
            result = self.explore_step(region)
            explored_count += 1
            
            # 打印结果
            print(f"   → {result['result']['change_type']}: {result['interpretation']}")
            
            # 如果页面发生重大变化，按返回键回到之前的页面
            if result["result"]["change_type"] == "major":
                print(f"   ← 按返回键...")
                self.press_back()
                time.sleep(1)
        
        # 保存结果
        self.save_exploration_results()
        
        return self.exploration_log


def start_exploration(device_port: int = 16384, max_steps: int = 15):
    """
    启动探索
    
    Args:
        device_port: 设备ADB端口
        max_steps: 最大探索步数
    """
    explorer = AIExplorer(device_port, output_dir="E:/UIAutotest/explorer_output")
    results = explorer.auto_explore(max_steps=max_steps)
    return results


if __name__ == "__main__":
    start_exploration()
