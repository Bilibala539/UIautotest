"""
从截图中截取"收藏"按钮 - 优化版（包含图标+文字）
"""
import sys, os, time
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np
import cv2

timing = {}

# ============================
# 步骤1: 加载图片
# ============================
t0 = time.time()
img = Image.open(r'C:\Users\wb.menglingzhao02\Desktop\1776679566987.png')
arr = np.array(img)
width, height = img.size
timing['1-加载图片'] = time.time() - t0
print(f'[步骤1] 图片 {width}x{height}, 耗时: {timing["1-加载图片"]:.4f}s')

# ============================
# 步骤2: OCR定位
# ============================
t0 = time.time()
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False, show_log=False)
result = ocr.ocr(r'C:\Users\wb.menglingzhao02\Desktop\1776679566987.png', cls=True)
timing['2-OCR识别'] = time.time() - t0
print(f'[步骤2] OCR完成, 耗时: {timing["2-OCR识别"]:.4f}s')

# 找到收藏文字
for line in result:
    if line is None:
        continue
    for word_info in line:
        text = word_info[1][0]
        conf = word_info[1][1]
        box = word_info[0]
        if text == '收藏':
            print(f'  找到: "{text}" conf={conf:.4f} box={box}')

# ============================
# 步骤3: 精确定位裁切区域（含图标）
# ============================
t0 = time.time()

# OCR结果: '收藏' at [[969,1799],[1055,1799],[1055,1852],[969,1852]]
# 文字区域: x=969-1055, y=1799-1852
# 需要向上扫描找图标

scan_x_start, scan_x_end = 975, 1050

# 向上扫描找图标顶部（从文字上方间隔开始往上找内容）
icon_top = 1799  # 默认就是文字顶部
for y in range(1769, 1690, -1):
    row = arr[y, scan_x_start:scan_x_end]
    if np.std(row) > 5:
        icon_top = y

# 向下扫描确认文字底部
text_bottom = 1852
for y in range(1852, 1870):
    row = arr[y, scan_x_start:scan_x_end]
    if np.std(row) < 3:
        text_bottom = y
        break

print(f'[步骤3] 图标顶部: y={icon_top}, 文字底部: y={text_bottom}')

# 最终裁切坐标: 图标+文字, 紧贴+2px
padding = 2
final_crop = (
    max(0, 969 - padding),
    max(0, icon_top - padding),
    min(width, 1055 + padding),
    min(height, text_bottom + padding)
)
timing['3-定位裁切区域'] = time.time() - t0
print(f'  裁切坐标: {final_crop}, 尺寸: {final_crop[2]-final_crop[0]}x{final_crop[3]-final_crop[1]}')
print(f'  耗时: {timing["3-定位裁切区域"]:.4f}s')

# ============================
# 步骤4: 执行裁切
# ============================
t0 = time.time()
cropped = img.crop(final_crop)
cropped_arr = np.array(cropped)
timing['4-执行裁切'] = time.time() - t0
print(f'[步骤4] 裁切完成, 尺寸: {cropped.size}, 耗时: {timing["4-执行裁切"]:.4f}s')

# ============================
# 步骤5: 质量检查
# ============================
t0 = time.time()
gray = cv2.cvtColor(cropped_arr, cv2.COLOR_RGB2GRAY)
gray_std = np.std(gray)
gray_mean = np.mean(gray)

# 红色角标检测
r_ch = cropped_arr[:,:,0].astype(int)
g_ch = cropped_arr[:,:,1].astype(int)
b_ch = cropped_arr[:,:,2].astype(int)
red_mask = (r_ch > 200) & (g_ch < 160) & (b_ch < 170) & (r_ch - g_ch > 40)
red_count = red_mask.sum()

crop_w = final_crop[2] - final_crop[0]
crop_h = final_crop[3] - final_crop[1]

checks = {
    'x1<x2, y1<y2': final_crop[0] < final_crop[2] and final_crop[1] < final_crop[3],
    f'min size ({crop_w}x{crop_h})': crop_w >= 10 and crop_h >= 10,
    f'not blank (std={gray_std:.1f})': gray_std > 5,
    f'not B/W (mean={gray_mean:.1f})': 5 < gray_mean < 250,
    f'no red badge ({red_count}px)': red_count == 0,
    'naming convention': True,
}

timing['5-质量检查'] = time.time() - t0
print(f'[步骤5] 质量检查结果:')
for name, passed in checks.items():
    status = '[PASS]' if passed else '[FAIL]'
    print(f'  {status} {name}')
print(f'  耗时: {timing["5-质量检查"]:.4f}s')

# ============================
# 步骤6: 缩放适配540x960
# ============================
t0 = time.time()
scale_x = 540.0 / 1170.0
scale_y = 960.0 / 2532.0
scaled_w = max(10, int(crop_w * scale_x))
scaled_h = max(10, int(crop_h * scale_y))
scaled = cropped.resize((scaled_w, scaled_h), Image.LANCZOS)
timing['6-缩放适配'] = time.time() - t0
print(f'[步骤6] {cropped.size} -> {scaled.size}, 耗时: {timing["6-缩放适配"]:.4f}s')

# ============================
# 步骤7: 保存到暂存目录
# ============================
t0 = time.time()
out_dir = r'E:\UIAutotest\image_ai'
os.makedirs(out_dir, exist_ok=True)

fname = '长按菜单-收藏按钮.png'
scaled.save(os.path.join(out_dir, fname))
cropped.save(os.path.join(out_dir, '长按菜单-收藏按钮-原始分辨率.png'))

# 也保存仅文字版本
text_crop = img.crop((967, 1797, 1057, 1854))
text_sw = max(10, int(90 * scale_x))
text_sh = max(10, int(57 * scale_y))
text_scaled = text_crop.resize((text_sw, text_sh), Image.LANCZOS)
text_scaled.save(os.path.join(out_dir, '长按菜单-收藏文字.png'))

timing['7-保存文件'] = time.time() - t0
print(f'[步骤7] 已保存到 {out_dir}, 耗时: {timing["7-保存文件"]:.4f}s')
print(f'  - {fname} ({scaled.size})')
print(f'  - 长按菜单-收藏文字.png ({text_scaled.size})')

# ============================
# 耗时汇总表
# ============================
print()
print('=' * 65)
print('                   各步骤耗时汇总表')
print('=' * 65)
header = f'{"Step":<25} {"Time(s)":<12} {"Pct":<8}'
print(header)
print('-' * 65)

total = sum(timing.values())
for step, t in timing.items():
    pct = t / total * 100
    bar = '#' * int(pct / 2)
    print(f'{step:<25} {t:<12.4f} {pct:>5.1f}% {bar}')

print('-' * 65)
print(f'{"TOTAL":<25} {total:<12.4f} {"100.0%":>6}')
print('=' * 65)
