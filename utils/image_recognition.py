"""
图像识别工具模块
提供基于OpenCV模板匹配的图像定位功能
"""

import cv2
import numpy as np
import os
from PIL import Image
from io import BytesIO
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class ImageRecognition:
    """图像识别工具类"""

    def __init__(self, driver, template_path: str = "./templates/"):
        """
        初始化图像识别工具

        Args:
            driver: Appium WebDriver实例
            template_path: 模板图片存储路径
        """
        self.driver = driver
        self.template_path = template_path
        self._ensure_template_dir()

    def _ensure_template_dir(self):
        """确保模板目录存在"""
        if not os.path.exists(self.template_path):
            os.makedirs(self.template_path)
            logger.info(f"创建模板目录: {self.template_path}")

    def take_screenshot(self) -> np.ndarray:
        """
        截取当前屏幕

        Returns:
            numpy.ndarray: 屏幕截图的numpy数组 (RGB格式)
        """
        try:
            screenshot = self.driver.get_screenshot_as_png()
            image = Image.open(BytesIO(screenshot))
            return np.array(image)
        except Exception as e:
            logger.error(f"截屏失败: {e}")
            raise

    def find_element_by_image(self, template_name: str, threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        通过图像匹配查找元素位置

        Args:
            template_name: 模板图片文件名（不含路径）
            threshold: 匹配阈值，范围0-1，默认0.8

        Returns:
            tuple: (x, y) 中心坐标，如果未找到返回None
        """
        template_path = os.path.join(self.template_path, template_name)

        if not os.path.exists(template_path):
            logger.error(f"模板图片不存在: {template_path}")
            return None

        try:
            screen_img = self.take_screenshot()
            template = cv2.imread(template_path, 0)

            if template is None:
                logger.error(f"无法加载模板图片: {template_path}")
                return None

            screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_RGB2GRAY)
            result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                h, w = template.shape
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                logger.debug(f"找到元素 {template_name} at ({center_x}, {center_y}), confidence: {max_val:.2f}")
                return (center_x, center_y)
            else:
                logger.debug(f"未找到元素 {template_name}, best match confidence: {max_val:.2f}")
                return None

        except Exception as e:
            logger.error(f"图像识别失败: {e}")
            return None

    def find_multiple_elements_by_image(self, template_name: str, threshold: float = 0.8) -> List[Tuple[int, int]]:
        """
        查找屏幕上所有匹配的元素位置

        Args:
            template_name: 模板图片文件名
            threshold: 匹配阈值

        Returns:
            list: 包含所有匹配位置的列表 [(x1, y1), (x2, y2), ...]
        """
        template_path = os.path.join(self.template_path, template_name)

        if not os.path.exists(template_path):
            logger.error(f"模板图片不存在: {template_path}")
            return []

        try:
            screen_img = self.take_screenshot()
            template = cv2.imread(template_path, 0)

            if template is None:
                logger.error(f"无法加载模板图片: {template_path}")
                return []

            screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_RGB2GRAY)
            result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)

            # 找到所有匹配点
            locations = np.where(result >= threshold)
            matches = []
            h, w = template.shape

            for pt in zip(*locations[::-1]):
                center_x = pt[0] + w // 2
                center_y = pt[1] + h // 2
                matches.append((center_x, center_y))

            logger.debug(f"找到 {len(matches)} 个匹配元素 {template_name}")
            return matches

        except Exception as e:
            logger.error(f"多元素图像识别失败: {e}")
            return []


# 便捷函数
def aw_find_by_image(driver, template_name: str, threshold: float = 0.8) -> Optional[Tuple[int, int]]:
    """
    便捷方法：通过图像查找元素位置

    Args:
        driver: Appium WebDriver实例
        template_name: 模板图片文件名
        threshold: 匹配阈值

    Returns:
        tuple: (x, y) 中心坐标，如果未找到返回None
    """
    image_recog = ImageRecognition(driver)
    return image_recog.find_element_by_image(template_name, threshold)


def aw_find_multiple_by_image(driver, template_name: str, threshold: float = 0.8) -> List[Tuple[int, int]]:
    """
    便捷方法：查找多个匹配元素

    Args:
        driver: Appium WebDriver实例
        template_name: 模板图片文件名
        threshold: 匹配阈值

    Returns:
        list: 匹配位置列表
    """
    image_recog = ImageRecognition(driver)
    return image_recog.find_multiple_elements_by_image(template_name, threshold)