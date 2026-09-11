# -*- coding: utf-8 -*-
"""一次性修复:pages/ 中滞留的 image_ai/flutter 路径与过期草稿标注(所有图已转正)"""
import glob, re, os

REPL = [
    # 播放页小节标题(无 .png,路径规则覆盖不到)
    ('image_ai/flutter 草稿，2026-09-10 aw-element Wave2 采集，待 verify 转正',
     'image/flutter，2026-09-10 aw-element Wave2 采集，已转正'),
    ('（2026-09-10 Wave1 采集，离线匹配 1.000，待 verify 转正）',
     '（2026-09-10 Wave1 采集，离线匹配 1.000，已转正）'),
    ('已采集，draft；⛔ 仅存在性断言用', '已转正；⛔ 仅存在性断言用'),
    ('已采集，draft；⛔ 同上', '已转正；⛔ 同上'),
    ('已采集，draft）', '已转正）'),
    ('已采集，draft；', '已转正；'),
    ('待 verify 转正', '已转正'),
    ('右上角扫一扫图标（草稿）', '右上角扫一扫图标'),
]

changed = {}
for f in glob.glob('knowledge/swan/pages/*.md'):
    text = open(f, encoding='utf-8').read()
    orig = text
    # 路径替换仅当目标文件真实存在于 image/flutter/
    def sub_path(m):
        name = m.group(1)
        if os.path.isfile(f'image/flutter/{name}'):
            return f'image/flutter/{name}'
        return m.group(0)
    text = re.sub(r'image_ai/flutter/([^ |）(]*\.png)', sub_path, text)
    for a, b in REPL:
        text = text.replace(a, b)
    if text != orig:
        open(f, 'w', encoding='utf-8', newline='').write(text)
        changed[os.path.basename(f)] = sum(1 for a, _ in REPL if a in orig) + (1 if 'image_ai/flutter' in orig else 0)

for k, v in changed.items():
    print('fixed:', k)
print('total files:', len(changed))
