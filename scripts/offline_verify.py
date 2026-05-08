"""
离线验证：使用保存的截图验证所有 image_ai 中的图片
"""
import cv2
import numpy as np
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
test_path = r"E:\UIAutotest\image_ai"


def match_against(img, name, threshold=0.8):
    fp = os.path.join(test_path, name)
    if not os.path.exists(fp):
        return "MISSING", 0.0
    template = cv2.imdecode(np.fromfile(fp, dtype=np.uint8), cv2.IMREAD_COLOR)
    if template is None:
        return "ERROR", 0.0
    if template.shape[0] > img.shape[0] or template.shape[1] > img.shape[1]:
        return "TOO_BIG", 0.0
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return ("PASS" if max_val >= threshold else "FAIL"), max_val


results = {}
print("=" * 80)
print("OFFLINE VERIFICATION")
print("=" * 80)

# 1. Contacts page
img1 = cv2.imread("screenshots/verify_contacts_page.png")
print("\n[Contacts Page]")
contacts_imgs = [
    "通讯录页-左上角通讯录文案.png", "通讯录页-搜索按钮.png", "通讯录页-添加按钮.png",
    "通讯录页-联系人分组入口.png", "通讯录页-群组入口.png", "通讯录页-服务号入口.png",
    "通讯录页-字母索引栏.png", "通讯录页-底部导航栏消息tab.png", "通讯录页-底部导航栏日历tab.png",
    "通讯录页-底部导航栏云空间tab.png", "通讯录页-底部导航栏工作台tab.png",
    "通讯录页-底部导航栏易生活tab.png", "通讯录页-底部导航栏更多tab.png",
]
for name in contacts_imgs:
    status, score = match_against(img1, name)
    results[name] = (status, score)
    mark = "OK" if status == "PASS" else "XX"
    print(f"  [{mark}] {name:<50} {score:.3f}")

# 2. Settings page
img2 = cv2.imread("screenshots/verify_settings_page.png")
if img2 is not None:
    print("\n[Settings Page]")
    status, score = match_against(img2, "设置页-消息入口.png")
    results["设置页-消息入口.png"] = (status, score)
    mark = "OK" if status == "PASS" else "XX"
    print(f"  [{mark}] {'设置页-消息入口.png':<50} {score:.3f}")

# 3. Message settings page
img3 = cv2.imread("screenshots/verify_msg_settings_page.png")
if img3 is not None:
    print("\n[Message Settings Page]")
    for name in ["消息设置页-页面标题消息.png", "消息设置页-开关-开启状态.png", "消息设置页-开关-关闭状态.png"]:
        status, score = match_against(img3, name)
        results[name] = (status, score)
        mark = "OK" if status == "PASS" else "XX"
        print(f"  [{mark}] {name:<50} {score:.3f}")

# 4. Chat + keyboard
img4 = cv2.imread("screenshots/chat_with_keyboard.png")
if img4 is not None:
    print("\n[Chat Page + Keyboard]")
    status, score = match_against(img4, "聊天页-段落按钮.png")
    results["聊天页-段落按钮.png"] = (status, score)
    mark = "OK" if status == "PASS" else "XX"
    print(f"  [{mark}] {'聊天页-段落按钮.png':<50} {score:.3f}")

# 5. Extended edit toolbar
img5 = cv2.imread("screenshots/extended_edit_toolbar.png")
if img5 is not None:
    print("\n[Extended Edit Toolbar]")
    ext_imgs = [
        "扩展编辑-加粗B按钮.png", "扩展编辑-斜体I按钮.png", "扩展编辑-下划线U按钮.png",
        "扩展编辑-删除线S按钮.png", "扩展编辑-字色A按钮.png", "扩展编辑-样式6按钮.png",
        "扩展编辑-Markdown按钮.png", "扩展编辑-发送按钮.png", "扩展编辑-关闭按钮.png",
        "扩展编辑-样式工具栏.png",
    ]
    for name in ext_imgs:
        status, score = match_against(img5, name)
        results[name] = (status, score)
        mark = "OK" if status == "PASS" else "XX"
        print(f"  [{mark}] {name:<50} {score:.3f}")

# 6. Long press menu
img6 = cv2.imread("screenshots/recrop_longpress_actual.png")
if img6 is not None:
    print("\n[Long Press Menu]")
    for name in ["长按菜单-收藏按钮.png", "长按菜单-收藏文字.png"]:
        status, score = match_against(img6, name)
        results[name] = (status, score)
        mark = "OK" if status == "PASS" else "XX"
        print(f"  [{mark}] {name:<50} {score:.3f}")

# Summary
print("\n" + "=" * 80)
passed = sum(1 for s, _ in results.values() if s == "PASS")
failed = sum(1 for s, _ in results.values() if s == "FAIL")
total = len(results)
print(f"SUMMARY: {passed}/{total} PASSED, {failed}/{total} FAILED")
print("=" * 80)

if failed > 0:
    print("\nSTILL FAILING:")
    for name, (status, score) in results.items():
        if status == "FAIL":
            print(f"  {name:<50} score={score:.3f}")
