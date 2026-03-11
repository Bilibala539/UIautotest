"""
从POPO消息页截图中裁切UI元素并保存到桌面
"""
import cv2
import os
import sys

# 源截图路径
source_image_path = r"E:\UIAutotest\image\POPO-screenshot-20260311-205115.png"

# 桌面路径
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

# 输出目录（桌面下的POPO元素截图文件夹）
output_dir = os.path.join(desktop_path, "POPO_Elements")
os.makedirs(output_dir, exist_ok=True)

# 读取原图
img = cv2.imread(source_image_path)
if img is None:
    print(f"[ERROR] Cannot read image: {source_image_path}")
    exit(1)

height, width = img.shape[:2]
print(f"[OK] Image size: {width} x {height}")

# 定义裁切区域 (x1, y1, x2, y2) 和文件名
# 基于截图分析的坐标（截图尺寸约 540 x 960）
elements = {
    # 顶部标题栏
    "msg_tab-top_left_avatar.png": (38, 95, 85, 142),
    "msg_tab-top_left_msg_text.png": (95, 95, 175, 145),
    "msg_tab-color_ring_status.png": (335, 95, 385, 145),
    "msg_tab-search_button.png": (405, 95, 455, 145),
    "msg_tab-add_button.png": (465, 95, 515, 145),
    
    # 顶部快捷用户区域
    "msg_tab-quick_user_avatar1.png": (25, 165, 100, 240),
    "msg_tab-quick_user_avatar2.png": (130, 165, 205, 240),
    "msg_tab-quick_user_avatar3.png": (235, 165, 310, 240),
    "msg_tab-quick_user_avatar4.png": (340, 165, 415, 240),
    "msg_tab-expand_button.png": (445, 165, 520, 240),
    
    # 会话列表-POPO助手
    "msg_tab-chat_avatar_popo_assistant.png": (25, 270, 100, 345),
    "msg_tab-unread_badge_num2.png": (75, 270, 110, 305),
    "msg_tab-chat_title_popo_assistant.png": (110, 280, 280, 320),
    "msg_tab-chat_time.png": (450, 280, 510, 320),
    
    # 会话列表-POPO通知服务测试群
    "msg_tab-chat_avatar_group_99plus.png": (25, 365, 100, 440),
    "msg_tab-unread_badge_99plus.png": (55, 365, 105, 400),
    "msg_tab-chat_title_group.png": (110, 375, 420, 410),
    "msg_tab-chat_summary_at_all.png": (110, 410, 510, 450),
    
    # 会话列表-工作日历
    "msg_tab-chat_avatar_work_calendar.png": (25, 460, 100, 535),
    "msg_tab-service_account_tag.png": (225, 480, 290, 515),
    
    # 会话列表-群管理助手
    "msg_tab-chat_avatar_group_manager.png": (25, 560, 100, 635),
    
    # 会话列表-机器人
    "msg_tab-chat_avatar_robot.png": (25, 660, 100, 735),
    "msg_tab-robot_tag.png": (390, 680, 465, 715),
    
    # 会话列表-悠哈哈
    "msg_tab-chat_avatar_personal.png": (25, 760, 100, 835),
    
    # 底部导航栏
    "msg_tab-bottom_nav_full.png": (0, 855, 540, 930),
    "msg_tab-nav_msg_blue_highlight.png": (25, 860, 95, 925),
    "msg_tab-nav_calendar_gray.png": (130, 860, 200, 925),
    "msg_tab-nav_workbench_gray.png": (235, 860, 305, 925),
    "msg_tab-nav_contacts_gray.png": (335, 860, 405, 925),
    "msg_tab-nav_more_gray.png": (440, 860, 510, 925),
}

# 执行裁切
success_count = 0
for filename, (x1, y1, x2, y2) in elements.items():
    # 边界检查
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(width, x2)
    y2 = min(height, y2)
    
    if x2 <= x1 or y2 <= y1:
        print(f"[SKIP] Invalid region: {filename}")
        continue
    
    # 裁切
    cropped = img[y1:y2, x1:x2]
    
    # 保存
    output_path = os.path.join(output_dir, filename)
    result = cv2.imwrite(output_path, cropped)
    if result:
        print(f"[OK] Saved: {filename}")
        success_count += 1
    else:
        print(f"[FAIL] Cannot save: {filename}")

print(f"\n[DONE] Completed! Cropped {success_count} elements")
print(f"[PATH] Output directory: {output_dir}")