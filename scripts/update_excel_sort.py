"""更新Excel - 标记群组排序用例通过"""
import sys, os
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
sys.stdout.reconfigure(encoding='utf-8')

import openpyxl
wb = openpyxl.load_workbook(r"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子.xlsx")
ws = wb.active

# Row 58: 默认排序
ws.cell(row=58, column=8).value = "test_group_sort_default.py"
# Row 59: 最后活跃由近及远
ws.cell(row=59, column=8).value = "test_group_sort_recent.py"
# Row 60: 最后活跃由远及近
ws.cell(row=60, column=8).value = "test_group_sort_oldest.py"

wb.save(r"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子.xlsx")
print("Rows 58-60 marked as PASSED!")
print("  Row 58: test_group_sort_default.py")
print("  Row 59: test_group_sort_recent.py")
print("  Row 60: test_group_sort_oldest.py")
