"""
从截图中截取"收藏"按钮的完整流程脚本
包含每个步骤的耗时统计
"""
import time
import os
import sys
import numpy as np
from PIL import Image

# 修复Windows控制台编码问题
sys.stdout.reconfigure(encoding='utf-8')

# 耗时统计字典
timing = {}

# ============================
# 步骤1: 加载源截图
# ============================
step_name = "步骤1: 加载源截图"
t0 = time.time()

source_path = r"C:\Users\wb.menglingzhao02\Desktop\1776679566987.png"
img = Image.open(source_path)
img_array = np.array(img)
width, height = img.size

timing[step_name] = time.time() - t0
print(f"[{step_name}] 图片尺寸: {width}x{height}, 模式: {img.mode}, 耗时: {timing[step_name]:.4f}s")

# ============================
# 步骤2: OCR识别定位"收藏"文字
# ============================
step_name = "步骤2: OCR识别定位'收藏'文字"
t0 = time.time()

from paddleocr import PaddleOCR
ocr_engine = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False, show_log=False)
ocr_result = ocr_engine.ocr(source_path, cls=True)

timing[step_name] = time.time() - t0

# 查找"收藏"相关的OCR结果
favorite_results = []
all_results = []
for line in ocr_result:
    if line is None:
        continue
    for word_info in line:
        box = word_info[0]
        text = word_info[1][0]
        confidence = word_info[1][1]
        all_results.append((text, confidence, box))
        if "收藏" in text:
            favorite_results.append((text, confidence, box))

print(f"[{step_name}] 识别到 {len(all_results)} 个文字区域, 耗时: {timing[step_name]:.4f}s")
print(f"  找到包含'收藏'的结果: {len(favorite_results)} 个")
for r in favorite_results:
    print(f"    文字: '{r[0]}', 置信度: {r[1]:.4f}, 位置: {r[2]}")

# ============================
# 步骤3: 分析页面上下文，确定目标元素
# ============================
step_name = "步骤3: 分析上下文确定目标元素"
t0 = time.time()

# 打印所有OCR结果以便分析页面结构
print(f"\n  === 页面所有OCR文字(用于分析上下文) ===")
for text, conf, box in sorted(all_results, key=lambda x: x[2][0][1]):  # 按y坐标排序
    y_center = (box[0][1] + box[2][1]) / 2
    x_center = (box[0][0] + box[2][0]) / 2
    print(f"    y={y_center:.0f} x={x_center:.0f} | '{text}' (conf={conf:.3f})")

# 选择最佳的"收藏"匹配
target = None
if favorite_results:
    # 如果有多个匹配，选择置信度最高的精确匹配
    exact_matches = [r for r in favorite_results if r[0] == "收藏"]
    if exact_matches:
        target = max(exact_matches, key=lambda x: x[1])
    else:
        target = max(favorite_results, key=lambda x: x[1])

timing[step_name] = time.time() - t0
if target:
    print(f"\n[{step_name}] 选定目标: '{target[0]}', 置信度: {target[1]:.4f}, 耗时: {timing[step_name]:.4f}s")
    print(f"  OCR box: {target[2]}")
else:
    print(f"\n[{step_name}] 未找到目标! 耗时: {timing[step_name]:.4f}s")
    sys.exit(1)

# ============================
# 步骤4: 计算裁切坐标（紧贴原则 + 安全边距）
# ============================
step_name = "步骤4: 计算裁切坐标"
t0 = time.time()

box = target[2]
# OCR box是四个角点: [左上, 右上, 右下, 左下]
x_min = min(p[0] for p in box)
x_max = max(p[0] for p in box)
y_min = min(p[1] for p in box)
y_max = max(p[1] for p in box)

# 扩展2px边距（紧贴原则）
padding = 2
x1 = max(0, int(x_min) - padding)
y1 = max(0, int(y_min) - padding)
x2 = min(width, int(x_max) + padding)
y2 = min(height, int(y_max) + padding)

# 但由于"收藏"按钮可能有图标+文字组合，需要检查周围是否有图标
# 先看OCR文字位置，判断是否为长按菜单中的按钮
# 长按菜单中的按钮通常有图标在文字上方
# 检查文字上方是否有非文字内容（图标区域）

# 分析: 收藏按钮通常在长按消息弹出的菜单中
# 菜单项布局: 上方是图标，下方是文字
# 需要将图标也包含在截取范围内

# 检查上方区域的颜色（看是否有图标）
text_y_center = (y_min + y_max) / 2
text_height = y_max - y_min

# 向上扩展，检查图标区域（通常图标在文字上方，约等于文字高度的1.5-2倍）
icon_check_y_start = max(0, int(y_min - text_height * 2.5))
icon_check_y_end = int(y_min)
icon_check_x_center = int((x_min + x_max) / 2)
icon_check_x_start = max(0, icon_check_x_center - int((x_max - x_min)))
icon_check_x_end = min(width, icon_check_x_center + int((x_max - x_min)))

# 检查上方区域是否有非背景像素（图标）
upper_region = img_array[icon_check_y_start:icon_check_y_end, icon_check_x_start:icon_check_x_end]
if upper_region.size > 0:
    gray_upper = np.mean(upper_region, axis=2)
    # 如果上方区域标准差较大，说明有内容（不全是纯色背景）
    has_icon = np.std(gray_upper) > 15
    print(f"  上方区域分析: y={icon_check_y_start}-{icon_check_y_end}, std={np.std(gray_upper):.1f}, 有图标: {has_icon}")
    
    if has_icon:
        # 如果有图标，扩展裁切范围包含图标
        # 但我们按照"宁小勿大"原则，只截取文字部分
        # 因为长按菜单中"收藏"通常OCR可以定位，用图标+文字截取匹配度可能更高
        # 这里我们提供两种裁切方案
        
        # 方案A: 只截取文字
        crop_text_only = (x1, y1, x2, y2)
        
        # 方案B: 包含图标 - 找到图标的实际上边界
        # 从文字上方向上扫描，找到内容的起始y
        for scan_y in range(icon_check_y_end - 1, icon_check_y_start, -1):
            row = img_array[scan_y, icon_check_x_start:icon_check_x_end]
            row_gray = np.mean(row, axis=1)
            row_std = np.std(row_gray)
            # 如果这行基本是纯色（标准差很小），说明到了图标上边界
            if row_std < 8 and np.std(row.reshape(-1, 3), axis=0).max() < 10:
                icon_top_y = scan_y + 1
                break
        else:
            icon_top_y = icon_check_y_start
        
        crop_with_icon = (x1, max(0, icon_top_y - padding), x2, y2)
        
        print(f"  方案A (仅文字): {crop_text_only}")
        print(f"  方案B (含图标): {crop_with_icon}")
        
        # 选择方案B - 包含图标，匹配更精确
        final_crop = crop_with_icon
    else:
        final_crop = (x1, y1, x2, y2)
else:
    final_crop = (x1, y1, x2, y2)

timing[step_name] = time.time() - t0
print(f"[{step_name}] 最终裁切坐标: {final_crop}, 尺寸: {final_crop[2]-final_crop[0]}x{final_crop[3]-final_crop[1]}, 耗时: {timing[step_name]:.4f}s")

# ============================
# 步骤5: 执行裁切
# ============================
step_name = "步骤5: 执行裁切"
t0 = time.time()

cropped_img = img.crop(final_crop)
cropped_array = np.array(cropped_img)

timing[step_name] = time.time() - t0
print(f"[{step_name}] 裁切完成, 尺寸: {cropped_img.size}, 耗时: {timing[step_name]:.4f}s")

# ============================
# 步骤6: 质量检查
# ============================
step_name = "步骤6: 质量检查"
t0 = time.time()

import cv2

# 转为灰度检查
gray = cv2.cvtColor(cropped_array, cv2.COLOR_RGB2GRAY)
gray_std = np.std(gray)
gray_mean = np.mean(gray)

checks = []
# 检查1: 坐标有效性
if final_crop[0] < final_crop[2] and final_crop[1] < final_crop[3]:
    checks.append(("坐标顺序正确", "[PASS] 通过"))
else:
    checks.append(("坐标顺序正确", "[FAIL] 失败"))

# 检查2: 最小尺寸
w = final_crop[2] - final_crop[0]
h = final_crop[3] - final_crop[1]
if w >= 10 and h >= 10:
    checks.append((f"最小尺寸 ({w}x{h})", "[PASS] 通过"))
else:
    checks.append((f"最小尺寸 ({w}x{h})", "[FAIL] 失败 (< 10x10)"))

# 检查3: 不是空白
if gray_std > 5:
    checks.append((f"非空白 (std={gray_std:.1f})", "[PASS] 通过"))
else:
    checks.append((f"非空白 (std={gray_std:.1f})", "[FAIL] 可能空白"))

# 检查4: 不是全黑/全白
if 5 < gray_mean < 250:
    checks.append((f"非全黑/全白 (mean={gray_mean:.1f})", "[PASS] 通过"))
else:
    checks.append((f"非全黑/全白 (mean={gray_mean:.1f})", "[FAIL] 失败"))

# 检查5: 红色角标检测
r, g, b = cropped_array[:,:,0].astype(int), cropped_array[:,:,1].astype(int), cropped_array[:,:,2].astype(int)
red_mask = (r > 200) & (g < 160) & (b < 170) & (r - g > 40)
red_count = red_mask.sum()
if red_count == 0:
    checks.append(("无红色角标", "[PASS] 通过"))
else:
    checks.append((f"无红色角标 ({red_count}px)", "[WARN] 检测到红色像素"))

# 检查6: 命名规范
filename = "长按菜单-收藏按钮.png"
if '-' in filename and filename.endswith('.png'):
    checks.append(("命名规范", f"[PASS] 通过 ({filename})"))
else:
    checks.append(("命名规范", "[FAIL] 失败"))

timing[step_name] = time.time() - t0
print(f"[{step_name}] 耗时: {timing[step_name]:.4f}s")
for check_name, result in checks:
    print(f"  {result} - {check_name}")

# ============================
# 步骤7: 缩放到540x960比例 (源图1170x2532)
# ============================
step_name = "步骤7: 缩放适配540x960"
t0 = time.time()

# 源图是 1170x2532, 目标比例 540x960
# 缩放比例
scale_x = 540.0 / 1170.0  # ≈ 0.4615
scale_y = 960.0 / 2532.0  # ≈ 0.3791
# 注意：源图比例和目标比例不完全一致

# 使用统一缩放（取较小比例保持内容完整）
# 不过对于元素截取来说，我们需要将截取的元素缩放到模拟器能匹配的尺寸
# 先计算在540x960坐标系下的位置
scaled_crop = (
    int(final_crop[0] * scale_x),
    int(final_crop[1] * scale_y),
    int(final_crop[2] * scale_x),
    int(final_crop[3] * scale_y)
)

# 缩放裁切后的图片
scaled_w = scaled_crop[2] - scaled_crop[0]
scaled_h = scaled_crop[3] - scaled_crop[1]
if scaled_w < 10:
    scaled_w = 10
if scaled_h < 10:
    scaled_h = 10

scaled_img = cropped_img.resize((scaled_w, scaled_h), Image.LANCZOS)

timing[step_name] = time.time() - t0
print(f"[{step_name}] 原始裁切: {cropped_img.size} -> 缩放后: {scaled_img.size}, 耗时: {timing[step_name]:.4f}s")
print(f"  缩放比例: x={scale_x:.4f}, y={scale_y:.4f}")
print(f"  540x960坐标系下位置: {scaled_crop}")

# ============================
# 步骤8: 保存到暂存目录
# ============================
step_name = "步骤8: 保存到暂存目录"
t0 = time.time()

output_dir = r"E:\UIAutotest\image_ai"
os.makedirs(output_dir, exist_ok=True)

# 保存缩放版本（用于模板匹配）
output_path_scaled = os.path.join(output_dir, filename)
scaled_img.save(output_path_scaled)

# 同时保存原始分辨率版本（作为参考）
output_path_original = os.path.join(output_dir, "长按菜单-收藏按钮-原始分辨率.png")
cropped_img.save(output_path_original)

timing[step_name] = time.time() - t0
print(f"[{step_name}] 耗时: {timing[step_name]:.4f}s")
print(f"  缩放版(用于匹配): {output_path_scaled}")
print(f"  原始版(参考): {output_path_original}")

# ============================
# 步骤9: 输出耗时汇总表
# ============================
print("\n" + "=" * 65)
print("                    各步骤耗时汇总表")
print("=" * 65)
print(f"{'步骤':<35} {'耗时(秒)':<12} {'占比':<8}")
print("-" * 65)

total_time = sum(timing.values())
for step, t in timing.items():
    pct = t / total_time * 100
    bar = "#" * int(pct / 2)
    print(f"{step:<35} {t:<12.4f} {pct:>5.1f}% {bar}")

print("-" * 65)
print(f"{'总计':<35} {total_time:<12.4f} {'100.0%':>6}")
print("=" * 65)
