"""
搜索区域常量定义模块

提供预定义的屏幕区域坐标常量，用于 OCR 和图像识别的区域限定。

使用示例:
    from utils.aw.search_region import H, V, C
    
    # 水平分区: H.UP (上半部分), H.DOWN (下半部分)
    user.click_text("确认", search_region=H.DOWN)
    
    # 垂直分区: V.LEFT (左半部分), V.RIGHT (右半部分)  
    user.click_image("button.png", search_region=V.LEFT)
    
    # 中心分区: C.CENTER (中心), C.VERTICAL (垂直中间), C.HORIZONTAL (水平中间)
    user.click_text("确定", search_region=C.CENTER)
    
    # 直接传入自定义坐标 (x, y, width, height)
    user.click_text("确认", search_region=(0, 0, 540, 300))

注意:
    以下常量基于 540x960 分辨率设计，如果模拟器分辨率不同，请自行调整或直接传入坐标元组
"""

# ==================== 屏幕分辨率 ====================
x = 540
y = 960


# ==================== Normal: 常规 ====================
class Normal:
    """
    水平分区 - 将屏幕分为上下两部分
    
    - H.UP: 上半部分
    - H.DOWN: 下半部分
    """
    ALL = (0, 0, x, y)
    HALF_UP = (0, 0, x, int(y / 2))
    HALF_DOWN = (0, int(y / 2), x, int(y / 2))
    HALF_LEFT = (0, 0, int(x / 2), y)
    HALF_RIGHT = (int(x / 2), 0, int(x / 2), y)
    CENTER_POP = (0, int(y / 4), x, int(y * 3 / 4))
    BOTTOM_NAV = (0, 890, x, 70)  # 底部导航栏区域 (y=890~960)


# ==================== Search: 大搜 ====================
class Search:
    # 大搜结果列表
    RESULT_LIST = (0, 198, x, y)
    # 大搜输入框
    RESULT_INPUT = (48, 42, 387, 99)
    # 最近搜索
    RECENT_SEARCH = (38, 168, 500, 340)
    # 搜索tab栏
    SEARCH_TAB = (0, 100, x, 159)

# ==================== V: 垂直分区 (左/右) ====================
class V:
    """
    垂直分区 - 将屏幕分为左右两部分

    - V.LEFT: 左半部分
    - V.RIGHT: 右半部分
    """


if __name__ == '__main__':
    print(type(Normal.HALF_UP))
