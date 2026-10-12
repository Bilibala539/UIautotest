# -*- coding: utf-8 -*-
"""修正映射表：按 run7/run8 最终口径更新 wifi 行与 collect[player]/shuffle 行状态。"""
import openpyxl

XLSX = r'C:\Users\menglz.SWANSPEAKERS\Desktop\回归用例_自动化映射_v2.xlsx'
SOURCE = r'C:\Users\menglz.SWANSPEAKERS\Desktop\回归用例_自动化映射.xlsx'
wb = openpyxl.load_workbook(SOURCE)
ws = wb['自动化映射']

# 用例编号 → (状态, 真机验证, 说明) 的修正
fixes = {
    14: ("已实现", "绿(rig实证)", "run7 play_all[wifi] 通过,音箱在线窗口实证"),
    22: ("已实现", "flake", "loop[wifi-shuffle] shuffle换曲瞬态,红绿红观察项"),
    24: ("已实现", "绿(rig实证)", "run2 seek[wifi] 通过"),
    26: ("已实现", "绿(rig实证)", "run5_close volume_adjust[wifi] 4/4 通过"),
    28: ("已实现", "绿(rig实证)", "run8 volume_key[wifi] 3/3 通过(弹层感知重探)"),
    44: ("已实现", "红(产品疑点)", "链路全通,死于QQ源起播6s停(VIP试听限制疑点,已入档)"),
}
fixed = []
for row in ws.iter_rows(min_row=2):
    num = row[0].value
    if num in fixes:
        st, ver, note = fixes[num]
        row[6].value = st
        row[7].value = ver
        row[8].value = note
        fixed.append(num)
wb.save(XLSX)
print('修正行:', fixed)
