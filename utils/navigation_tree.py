"""
POPO应用导航树 - 用树形结构记录UI操作路径
支持从目标状态反推完整操作流程
"""

import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict


@dataclass
class ActionStep:
    """操作步骤"""
    type: str  # tap, swipe, keyevent, launch, wait
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    
    def to_adb_command(self, device_serial: str = "127.0.0.1:16384") -> str:
        """转换为ADB命令"""
        adb = r"D:\MuMuPlayer\nx_main\adb.exe"
        
        if self.type == "tap":
            x, y = self.params.get("x", 0), self.params.get("y", 0)
            return f'{adb} -s {device_serial} shell input tap {x} {y}'
        elif self.type == "swipe":
            x1, y1 = self.params.get("x1", 0), self.params.get("y1", 0)
            x2, y2 = self.params.get("x2", 0), self.params.get("y2", 0)
            duration = self.params.get("duration", 300)
            return f'{adb} -s {device_serial} shell input swipe {x1} {y1} {x2} {y2} {duration}'
        elif self.type == "keyevent":
            key = self.params.get("key", 4)  # 4 = BACK
            return f'{adb} -s {device_serial} shell input keyevent {key}'
        elif self.type == "launch":
            package = self.params.get("package", "com.netease.popo")
            return f'{adb} -s {device_serial} shell monkey -p {package} -c android.intent.category.LAUNCHER 1'
        elif self.type == "wait":
            seconds = self.params.get("seconds", 1)
            return f'# 等待 {seconds} 秒'
        return ""


@dataclass 
class NavNode:
    """导航树节点"""
    id: str
    name: str
    type: str  # root, page, element, action, state
    description: str = ""
    action: Optional[ActionStep] = None  # 到达此节点需要执行的操作
    screenshot: str = ""  # 截图路径
    children: List['NavNode'] = field(default_factory=list)
    
    def add_child(self, child: 'NavNode') -> 'NavNode':
        """添加子节点"""
        self.children.append(child)
        return child
    
    def find_node(self, target_id: str) -> Optional['NavNode']:
        """按ID查找节点"""
        if self.id == target_id:
            return self
        for child in self.children:
            result = child.find_node(target_id)
            if result:
                return result
        return None
    
    def find_by_name(self, name: str) -> Optional['NavNode']:
        """按名称查找节点（模糊匹配）"""
        if name.lower() in self.name.lower() or self.name.lower() in name.lower():
            return self
        for child in self.children:
            result = child.find_by_name(name)
            if result:
                return result
        return None
    
    def get_path_to(self, target_id: str, current_path: List['NavNode'] = None) -> Optional[List['NavNode']]:
        """获取从当前节点到目标节点的路径"""
        if current_path is None:
            current_path = []
        
        current_path = current_path + [self]
        
        if self.id == target_id:
            return current_path
        
        for child in self.children:
            result = child.get_path_to(target_id, current_path)
            if result:
                return result
        
        return None
    
    def get_all_leaves(self) -> List['NavNode']:
        """获取所有叶子节点"""
        if not self.children:
            return [self]
        
        leaves = []
        for child in self.children:
            leaves.extend(child.get_all_leaves())
        return leaves
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "action": asdict(self.action) if self.action else None,
            "screenshot": self.screenshot,
            "children": [child.to_dict() for child in self.children]
        }


class NavigationTree:
    """POPO导航树"""
    
    def __init__(self):
        self.root = self._build_tree()
    
    def _build_tree(self) -> NavNode:
        """构建POPO应用的导航树"""
        
        # 根节点：桌面
        root = NavNode(
            id="desktop",
            name="桌面",
            type="root",
            description="MuMu模拟器桌面"
        )
        
        # POPO应用入口
        popo = root.add_child(NavNode(
            id="popo_app",
            name="网易POPO",
            type="page",
            description="POPO应用主页（消息列表）",
            action=ActionStep("tap", {"x": 75, "y": 350}, "点击POPO图标"),
            screenshot="explore_09_reenter.png"
        ))
        
        # ========== 消息页面 ==========
        msg_page = popo.add_child(NavNode(
            id="message_page",
            name="消息页面",
            type="page",
            description="消息列表页面，显示所有会话"
        ))
        
        # --- 底部导航栏 ---
        nav_bar = msg_page.add_child(NavNode(
            id="nav_bar",
            name="底部导航栏",
            type="element",
            description="底部5个导航Tab"
        ))
        
        # 消息Tab（当前页面）
        nav_bar.add_child(NavNode(
            id="nav_message",
            name="消息Tab",
            type="element",
            description="底部导航-消息（当前高亮）",
            action=ActionStep("tap", {"x": 54, "y": 900}, "点击消息Tab")
        ))
        
        # 日历Tab
        calendar_page = nav_bar.add_child(NavNode(
            id="nav_calendar",
            name="日历Tab",
            type="page",
            description="日历视图，显示日程安排",
            action=ActionStep("tap", {"x": 162, "y": 900}, "点击日历Tab"),
            screenshot="explore_01_calendar.png"
        ))
        
        # 日历页面的子功能
        calendar_page.add_child(NavNode(
            id="calendar_add",
            name="新建日程",
            type="action",
            description="右下角蓝色+号，创建新日程",
            action=ActionStep("tap", {"x": 480, "y": 770}, "点击添加日程按钮")
        ))
        
        # 工作台Tab
        workspace_page = nav_bar.add_child(NavNode(
            id="nav_workspace",
            name="工作台Tab",
            type="page",
            description="工作台页面",
            action=ActionStep("tap", {"x": 270, "y": 900}, "点击工作台Tab"),
            screenshot="explore_02_workspace.png"
        ))
        
        # 通讯录Tab
        contacts_page = nav_bar.add_child(NavNode(
            id="nav_contacts",
            name="通讯录Tab",
            type="page",
            description="通讯录页面，联系人列表",
            action=ActionStep("tap", {"x": 378, "y": 900}, "点击通讯录Tab"),
            screenshot="explore_03_contacts.png"
        ))
        
        # 通讯录子功能
        contacts_page.add_child(NavNode(
            id="contacts_group",
            name="联系人分组",
            type="action",
            description="查看联系人分组",
            action=ActionStep("tap", {"x": 270, "y": 150}, "点击联系人分组")
        ))
        contacts_page.add_child(NavNode(
            id="contacts_teams",
            name="群组",
            type="action",
            description="查看群组列表",
            action=ActionStep("tap", {"x": 270, "y": 235}, "点击群组")
        ))
        contacts_page.add_child(NavNode(
            id="contacts_service",
            name="服务号",
            type="action",
            description="查看服务号列表",
            action=ActionStep("tap", {"x": 270, "y": 320}, "点击服务号")
        ))
        
        # 更多Tab（弹窗）
        more_panel = nav_bar.add_child(NavNode(
            id="nav_more",
            name="更多Tab",
            type="element",
            description="弹出更多应用面板",
            action=ActionStep("tap", {"x": 486, "y": 900}, "点击更多Tab"),
            screenshot="explore_04_more.png"
        ))
        
        # 更多面板中的应用
        more_panel.add_child(NavNode(
            id="more_meeting",
            name="会议",
            type="action",
            description="发起/加入会议",
            action=ActionStep("tap", {"x": 67, "y": 600}, "点击会议")
        ))
        more_panel.add_child(NavNode(
            id="more_task",
            name="任务",
            type="action", 
            description="任务管理",
            action=ActionStep("tap", {"x": 202, "y": 600}, "点击任务")
        ))
        more_panel.add_child(NavNode(
            id="more_cloud",
            name="云空间",
            type="action",
            description="云存储空间",
            action=ActionStep("tap", {"x": 337, "y": 600}, "点击云空间")
        ))
        
        # --- 顶部操作区 ---
        header = msg_page.add_child(NavNode(
            id="header",
            name="顶部操作区",
            type="element",
            description="顶部标题栏和操作按钮"
        ))
        
        # 用户头像 -> 侧边栏
        sidebar = header.add_child(NavNode(
            id="sidebar",
            name="侧边栏",
            type="element",
            description="个人中心侧边栏（抽屉菜单）",
            action=ActionStep("tap", {"x": 47, "y": 72}, "点击用户头像"),
            screenshot="explore_12_avatar.png"
        ))
        
        # 侧边栏功能
        sidebar.add_child(NavNode(
            id="sidebar_status",
            name="工作状态",
            type="action",
            description="设置工作状态",
            action=ActionStep("tap", {"x": 360, "y": 113}, "点击工作状态")
        ))
        sidebar.add_child(NavNode(
            id="sidebar_card",
            name="工卡",
            type="action",
            description="查看工卡信息",
            action=ActionStep("tap", {"x": 380, "y": 205}, "点击工卡")
        ))
        sidebar.add_child(NavNode(
            id="sidebar_favorite",
            name="我的收藏",
            type="action",
            description="查看收藏内容",
            action=ActionStep("tap", {"x": 143, "y": 395}, "点击我的收藏")
        ))
        sidebar.add_child(NavNode(
            id="sidebar_help",
            name="帮助与反馈",
            type="action",
            description="帮助中心和反馈入口",
            action=ActionStep("tap", {"x": 155, "y": 467}, "点击帮助与反馈")
        ))
        sidebar.add_child(NavNode(
            id="sidebar_devices",
            name="登录设备管理",
            type="action",
            description="管理已登录的设备",
            action=ActionStep("tap", {"x": 168, "y": 543}, "点击登录设备管理")
        ))
        
        # 设置页面
        settings_page = sidebar.add_child(NavNode(
            id="settings_page",
            name="设置",
            type="page",
            description="应用设置页面",
            action=ActionStep("tap", {"x": 118, "y": 620}, "点击设置"),
            screenshot="explore_13_settings.png"
        ))
        
        # 设置项
        settings_page.add_child(NavNode(
            id="settings_general",
            name="通用设置",
            type="action",
            description="通用设置选项",
            action=ActionStep("tap", {"x": 270, "y": 167}, "点击通用")
        ))
        settings_page.add_child(NavNode(
            id="settings_privacy",
            name="隐私设置",
            type="action",
            description="隐私相关设置",
            action=ActionStep("tap", {"x": 270, "y": 249}, "点击隐私")
        ))
        settings_page.add_child(NavNode(
            id="settings_calendar",
            name="日历设置",
            type="action",
            description="日历相关设置",
            action=ActionStep("tap", {"x": 270, "y": 330}, "点击日历")
        ))
        settings_page.add_child(NavNode(
            id="settings_message",
            name="消息设置",
            type="action",
            description="消息通知设置",
            action=ActionStep("tap", {"x": 270, "y": 411}, "点击消息")
        ))
        settings_page.add_child(NavNode(
            id="settings_notification",
            name="通知设置",
            type="action",
            description="推送通知设置",
            action=ActionStep("tap", {"x": 270, "y": 493}, "点击通知")
        ))
        settings_page.add_child(NavNode(
            id="settings_security",
            name="账号安全",
            type="action",
            description="账号安全设置",
            action=ActionStep("tap", {"x": 270, "y": 612}, "点击账号安全")
        ))
        settings_page.add_child(NavNode(
            id="settings_about",
            name="关于POPO",
            type="action",
            description="应用信息和版本",
            action=ActionStep("tap", {"x": 270, "y": 733}, "点击关于POPO")
        ))
        
        # 退出登录（需要先滚动）
        logout = settings_page.add_child(NavNode(
            id="logout",
            name="退出登录",
            type="action",
            description="退出当前账号",
            action=ActionStep("tap", {"x": 270, "y": 850}, "点击退出登录"),
            screenshot="explore_14_scroll.png"
        ))
        
        # 退出登录确认弹窗
        logout.add_child(NavNode(
            id="logout_confirm",
            name="确认退出登录",
            type="state",
            description="点击确认退出账号",
            action=ActionStep("tap", {"x": 380, "y": 540}, "点击确认退出")
        ))
        
        # SOS求助
        sidebar.add_child(NavNode(
            id="sidebar_sos",
            name="一键求助",
            type="action",
            description="紧急求助功能",
            action=ActionStep("tap", {"x": 108, "y": 885}, "点击一键求助SOS")
        ))
        
        # 搜索页面
        search_page = header.add_child(NavNode(
            id="search_page",
            name="搜索",
            type="page",
            description="全局搜索页面",
            action=ActionStep("tap", {"x": 432, "y": 72}, "点击搜索按钮"),
            screenshot="explore_10_search.png"
        ))
        
        # 搜索分类
        search_page.add_child(NavNode(
            id="search_all",
            name="搜索全部",
            type="element",
            description="搜索所有类型",
            action=ActionStep("tap", {"x": 48, "y": 132}, "点击全部Tab")
        ))
        search_page.add_child(NavNode(
            id="search_contacts",
            name="搜索联系人",
            type="element",
            description="只搜索联系人",
            action=ActionStep("tap", {"x": 134, "y": 132}, "点击联系人Tab")
        ))
        search_page.add_child(NavNode(
            id="search_groups",
            name="搜索群",
            type="element",
            description="只搜索群组",
            action=ActionStep("tap", {"x": 213, "y": 132}, "点击群Tab")
        ))
        search_page.add_child(NavNode(
            id="search_messages",
            name="搜索消息",
            type="element",
            description="只搜索消息内容",
            action=ActionStep("tap", {"x": 284, "y": 132}, "点击消息Tab")
        ))
        search_page.add_child(NavNode(
            id="search_ai",
            name="问AI",
            type="element",
            description="AI助手搜索",
            action=ActionStep("tap", {"x": 476, "y": 132}, "点击问AI")
        ))
        
        # 添加菜单
        add_menu = header.add_child(NavNode(
            id="add_menu",
            name="添加菜单",
            type="element",
            description="顶部+号下拉菜单",
            action=ActionStep("tap", {"x": 490, "y": 70}, "点击添加按钮"),
            screenshot="explore_11b_add.png"
        ))
        
        # 添加菜单选项
        add_menu.add_child(NavNode(
            id="add_contact",
            name="添加联系人",
            type="action",
            description="添加新联系人",
            action=ActionStep("tap", {"x": 392, "y": 163}, "点击添加联系人")
        ))
        add_menu.add_child(NavNode(
            id="join_group",
            name="加入群组",
            type="action",
            description="加入已有群组",
            action=ActionStep("tap", {"x": 378, "y": 232}, "点击加入群组")
        ))
        add_menu.add_child(NavNode(
            id="create_group",
            name="创建群组",
            type="action",
            description="创建新群组",
            action=ActionStep("tap", {"x": 378, "y": 303}, "点击创建群组")
        ))
        add_menu.add_child(NavNode(
            id="start_meeting",
            name="发起会议",
            type="action",
            description="发起视频/语音会议",
            action=ActionStep("tap", {"x": 378, "y": 372}, "点击发起会议")
        ))
        add_menu.add_child(NavNode(
            id="join_meeting",
            name="加入会议",
            type="action",
            description="加入已有会议",
            action=ActionStep("tap", {"x": 378, "y": 443}, "点击加入会议")
        ))
        add_menu.add_child(NavNode(
            id="ai_notes",
            name="开始AI听记",
            type="action",
            description="AI会议记录功能",
            action=ActionStep("tap", {"x": 392, "y": 512}, "点击开始AI听记")
        ))
        add_menu.add_child(NavNode(
            id="invite_external",
            name="邀请外部用户",
            type="action",
            description="邀请外部人员",
            action=ActionStep("tap", {"x": 400, "y": 583}, "点击邀请外部用户")
        ))
        add_menu.add_child(NavNode(
            id="scan_qr",
            name="扫一扫",
            type="action",
            description="扫描二维码",
            action=ActionStep("tap", {"x": 365, "y": 652}, "点击扫一扫")
        ))
        
        # --- 消息列表区 ---
        msg_list = msg_page.add_child(NavNode(
            id="message_list",
            name="消息列表",
            type="element",
            description="会话列表区域"
        ))
        
        # 会话项 -> 聊天详情
        chat_detail = msg_list.add_child(NavNode(
            id="chat_detail",
            name="聊天详情页",
            type="page",
            description="进入聊天对话页面",
            action=ActionStep("tap", {"x": 270, "y": 285}, "点击会话项"),
            screenshot="explore_06_chat.png"
        ))
        
        # 聊天详情页功能
        chat_detail.add_child(NavNode(
            id="chat_send_message",
            name="发送消息",
            type="action",
            description="在输入框输入并发送消息",
            action=ActionStep("tap", {"x": 270, "y": 860}, "点击输入框")
        ))
        chat_detail.add_child(NavNode(
            id="chat_voice",
            name="语音消息",
            type="action",
            description="发送语音消息",
            action=ActionStep("tap", {"x": 40, "y": 930}, "点击语音按钮")
        ))
        chat_detail.add_child(NavNode(
            id="chat_emoji",
            name="表情",
            type="action",
            description="发送表情",
            action=ActionStep("tap", {"x": 224, "y": 930}, "点击表情按钮")
        ))
        chat_detail.add_child(NavNode(
            id="chat_at",
            name="@提醒",
            type="action",
            description="@群成员",
            action=ActionStep("tap", {"x": 316, "y": 930}, "点击@按钮")
        ))
        chat_detail.add_child(NavNode(
            id="chat_more",
            name="更多功能",
            type="action",
            description="更多聊天功能",
            action=ActionStep("tap", {"x": 500, "y": 930}, "点击+号展开更多")
        ))
        
        return root
    
    def find_path_to_target(self, target_name: str) -> Optional[List[NavNode]]:
        """根据目标名称查找完整操作路径"""
        # 先找到目标节点
        target = self.root.find_by_name(target_name)
        if not target:
            return None
        
        # 获取从根到目标的路径
        return self.root.get_path_to(target.id)
    
    def get_operation_steps(self, target_name: str) -> List[Dict]:
        """获取到达目标的操作步骤"""
        path = self.find_path_to_target(target_name)
        if not path:
            return []
        
        steps = []
        for i, node in enumerate(path):
            if node.action:
                steps.append({
                    "step": len(steps) + 1,
                    "target": node.name,
                    "action": node.action.description,
                    "adb_command": node.action.to_adb_command(),
                    "expected_result": node.description
                })
        
        return steps
    
    def print_path_to_target(self, target_name: str):
        """打印到达目标的完整路径"""
        path = self.find_path_to_target(target_name)
        
        if not path:
            print(f"[ERROR] 未找到目标: {target_name}")
            return
        
        print(f"\n{'='*60}")
        print(f"目标: {target_name}")
        print(f"{'='*60}")
        print(f"\n操作路径: {' → '.join([n.name for n in path])}\n")
        
        steps = self.get_operation_steps(target_name)
        print("操作步骤:")
        print("-" * 60)
        
        for step in steps:
            print(f"\n步骤 {step['step']}: {step['target']}")
            print(f"  操作: {step['action']}")
            print(f"  命令: {step['adb_command']}")
            print(f"  预期: {step['expected_result']}")
        
        print(f"\n{'='*60}")
    
    def list_all_targets(self) -> List[str]:
        """列出所有可达的目标（叶子节点）"""
        leaves = self.root.get_all_leaves()
        return [leaf.name for leaf in leaves]
    
    def export_tree(self, filepath: str = "navigation_tree.json"):
        """导出导航树为JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.root.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"导航树已导出到: {filepath}")
    
    def generate_test_script(self, target_name: str) -> str:
        """生成到达目标的测试脚本"""
        steps = self.get_operation_steps(target_name)
        if not steps:
            return f"# 未找到目标: {target_name}"
        
        script = f'''"""
自动生成的测试脚本 - 目标: {target_name}
"""
import subprocess
import time

ADB = r"D:\\MuMuPlayer\\nx_main\\adb.exe"
DEVICE = "127.0.0.1:16384"

def run_adb(cmd):
    """执行ADB命令"""
    full_cmd = f'{{ADB}} -s {{DEVICE}} {{cmd}}'
    subprocess.run(full_cmd, shell=True, timeout=30)
    time.sleep(1.5)

def main():
    print("开始执行: 导航到 {target_name}")
    
'''
        for step in steps:
            script += f'''    # 步骤 {step["step"]}: {step["target"]}
    print("执行: {step["action"]}")
    run_adb("{step["adb_command"].split(" ", 3)[-1]}")
    
'''
        
        script += '''    print("完成!")

if __name__ == "__main__":
    main()
'''
        return script


# ============ 便捷函数 ============

def find_path(target: str):
    """查找到达目标的路径"""
    tree = NavigationTree()
    tree.print_path_to_target(target)


def list_targets():
    """列出所有可用目标"""
    tree = NavigationTree()
    targets = tree.list_all_targets()
    print("\n可用的目标列表:")
    print("-" * 40)
    for i, t in enumerate(targets, 1):
        print(f"  {i}. {t}")
    print(f"\n共 {len(targets)} 个目标")


def generate_script(target: str, save_path: str = None):
    """生成测试脚本"""
    tree = NavigationTree()
    script = tree.generate_test_script(target)
    
    if save_path:
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(script)
        print(f"脚本已保存到: {save_path}")
    else:
        print(script)


# ============ 主程序 ============

if __name__ == "__main__":
    # 创建导航树
    tree = NavigationTree()
    
    # 导出为JSON
    tree.export_tree("E:/UIAutotest/explorer_output/navigation_tree.json")
    
    # 示例：查找路径
    print("\n" + "="*60)
    print("示例1: 如何退出登录?")
    tree.print_path_to_target("退出登录")
    
    print("\n" + "="*60)
    print("示例2: 如何创建群组?")
    tree.print_path_to_target("创建群组")
    
    print("\n" + "="*60)
    print("示例3: 如何发送消息?")
    tree.print_path_to_target("发送消息")
