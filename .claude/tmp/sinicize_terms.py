# -*- coding: utf-8 -*-
"""知识库文档英文术语中文化扫描。
保护:YAML frontmatter 字段名、``` 代码块、`行内代码`(key 值/AW 方法名/路径)、目录路径 draft/ pages/。
只改描述性术语。"""
import glob, re, os, sys

RULES = [
    # (regex, replacement)
    (r'accessibility key', '无障碍键'),
    (r'accessibility resource-id', '无障碍资源标识'),
    (r'accessibility', '无障碍'),
    (r'bottom sheet', '底部弹层'),
    (r'(?<![A-Za-z_])sheet(?![A-Za-z_/])', '弹层'),
    (r'(?<![A-Za-z_/])dialog(?![A-Za-z_/])', '弹窗'),
    (r'(?<![A-Za-z_])clickable(?![A-Za-z_/])', '可点击'),
    (r'(?<![A-Za-z_/])bounds(?![A-Za-z_/])', '坐标范围'),
    (r'(status:\s*)draft\b', r'\g<1>草稿'),
    (r'(status:\s*)verified\b', r'\g<1>已验证'),
    (r'(type:\s*)screen\b', r'\g<1>页面'),
    (r'(?<![A-Za-z_./])verified(?![A-Za-z_/])', '已验证'),
    (r'(?<![A-Za-z_/])static(?![A-Za-z_/])', '静态'),
    (r'(?<![A-Za-z_/])dynamic(?![A-Za-z_/])', '动态'),
    (r'(?<![A-Za-z_./])draft(?![A-Za-z_/=])', '草稿'),
    (r'(?<![A-Za-z_.])promote(?![A-Za-z_])', '转正'),
    (r'(?<![A-Za-z_.])promoted(?![A-Za-z_])', '已转正'),
    (r'（key，', '（无障碍键，'),
    (r'（key）', '（无障碍键）'),
    (r'（key; ', '（无障碍键；'),
    (r'\| key \|', '| 无障碍键 |'),
    (r'\| key$', '| 无障碍键'),
    (r'无 key', '无无障碍键'),
    (r'有 key', '有无障碍键'),
    (r'走 key ', '走无障碍键 '),
    (r'key 与相机权限同族', '无障碍键与相机权限同族'),
    (r'可直接 key 断言', '可直接无障碍键断言'),
    (r'该 key 前先', '该无障碍键前先'),
    (r'判该 key ', '判该无障碍键 '),
    (r'key `login_submit_button`', '无障碍键 `login_submit_button`'),
    (r'key `wifi_device_card_<UUID>`', '无障碍键 `wifi_device_card_<UUID>`'),
    (r'语义 key', '语义无障碍键'),
    (r'元素 key', '元素无障碍键'),
    (r'（desc=', '（desc='),  # keep desc=
]

# frontmatter 行单独处理:只做 status/type 值替换,不碰字段名
FM_RULES = [
    (r'^(status:\s*)draft\s*$', r'\g<1>草稿'),
    (r'^(status:\s*)verified\s*$', r'\g<1>已验证'),
    (r'^(type:\s*)screen\s*$', r'\g<1>页面'),
    (r'^(type:\s*)sheet\s*$', r'\g<1>弹层'),
    (r'^(type:\s*)dialog\s*$', r'\g<1>弹窗'),
    (r'^(status:\s*)page\s*$', r'\g<1>页面'),
]

CODE_RE = re.compile(r'`[^`]*`')
FENCE_RE = re.compile(r'^```')

changed_files = 0
residual = []

for f in glob.glob('knowledge/swan/**/*.md', recursive=True):
    lines = open(f, encoding='utf-8').read().split('\n')
    in_fence = False
    in_fm = False
    fm_done = False
    out = []
    file_changed = False
    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        # frontmatter 区间
        if not fm_done and line.strip() == '---':
            in_fm = not in_fm
            if not in_fm:
                fm_done = True
            out.append(line)
            continue
        if in_fm:
            new = line
            for pat, rep in FM_RULES:
                new = re.sub(pat, rep, new)
            if new != line:
                file_changed = True
            out.append(new)
            continue
        # 正文:按反引号分段,只在非代码段应用规则
        parts = CODE_RE.split(line)
        seps = CODE_RE.findall(line)
        new_parts = []
        for seg in parts:
            s = seg
            for pat, rep in RULES:
                s = re.sub(pat, rep, s)
            new_parts.append(s)
        new = ''.join(''.join(pair) for pair in zip(new_parts, seps + ['']))
        if new != line:
            file_changed = True
        out.append(new)
    if file_changed:
        open(f, 'w', encoding='utf-8', newline='').write('\n'.join(out))
        changed_files += 1

print('changed files:', changed_files)
