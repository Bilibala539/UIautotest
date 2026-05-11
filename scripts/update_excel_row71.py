"""更新Excel - Row 71 标记通过，然后探索群组排序"""
import sys, os
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
sys.stdout.reconfigure(encoding='utf-8')

import openpyxl
wb = openpyxl.load_workbook(r"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子.xlsx")
ws = wb.active

# Row 71 passed
ws.cell(row=71, column=8).value = "test_sidebar_display.py"
print("Row 71: Marked as PASSED (test_sidebar_display.py)")

wb.save(r"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子.xlsx")
print("Excel saved!")
