"""平台隔离的图片路径与图片转正工具。

图片按 ``image/<platform>`` 与 ``image_ai/<platform>`` 分开保存。新截图
先登记到草稿目录，验证通过后调用 ``promote_image`` 转移到正式目录。
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORMAL_IMAGE_ROOT = PROJECT_ROOT / "image"
DRAFT_IMAGE_ROOT = PROJECT_ROOT / "image_ai"
SUPPORTED_PLATFORMS = ("web", "android", "flutter")


def normalize_platform(platform: Optional[str] = None) -> str:
    """返回受支持的平台名称。"""
    value = (platform or os.environ.get("PLATFORM", "web")).strip().lower()
    if value not in SUPPORTED_PLATFORMS:
        raise ValueError(
            f"不支持的平台: {value!r}；可选值: {', '.join(SUPPORTED_PLATFORMS)}"
        )
    return value


def get_image_dir(platform: Optional[str] = None, draft: bool = False) -> Path:
    """获取指定平台的正式或草稿图片目录，并确保目录存在。"""
    root = DRAFT_IMAGE_ROOT if draft else FORMAL_IMAGE_ROOT
    directory = root / normalize_platform(platform)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def image_path(
    filename: str,
    platform: Optional[str] = None,
    draft: bool = False,
) -> str:
    """生成平台图片路径，禁止路径穿越和绝对路径覆盖。"""
    relative_path = Path(filename)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError("图片文件名必须是平台目录内的相对路径")
    root = get_image_dir(platform, draft=draft).resolve()
    candidate = (root / relative_path).resolve()
    if root != candidate and root not in candidate.parents:
        raise ValueError("图片路径必须位于平台图片目录内")
    candidate.parent.mkdir(parents=True, exist_ok=True)
    return str(candidate)


def promote_image(
    filename: str,
    platform: Optional[str] = None,
    overwrite: bool = False,
) -> str:
    """将平台图片从 image_ai 转正到 image，并返回正式路径。"""
    source = Path(image_path(filename, platform=platform, draft=True))
    target = Path(image_path(filename, platform=platform, draft=False))
    if not source.is_file():
        raise FileNotFoundError(f"找不到待转正图片: {source}")
    if target.exists() and not overwrite:
        raise FileExistsError(f"正式图片已存在: {target}；如需覆盖请传入 overwrite=True")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))
    return str(target)


def demote_image(filename: str, platform: Optional[str] = None, overwrite: bool = False) -> str:
    """将平台图片从 image 退回 image_ai，便于重新验证。"""
    source = Path(image_path(filename, platform=platform, draft=False))
    target = Path(image_path(filename, platform=platform, draft=True))
    if not source.is_file():
        raise FileNotFoundError(f"找不到正式图片: {source}")
    if target.exists() and not overwrite:
        raise FileExistsError(f"草稿图片已存在: {target}；如需覆盖请传入 overwrite=True")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))
    return str(target)


CURRENT_PLATFORM = normalize_platform()
WEB_IMAGE_DIR = str(get_image_dir("web"))
ANDROID_IMAGE_DIR = str(get_image_dir("android"))
FLUTTER_IMAGE_DIR = str(get_image_dir("flutter"))
WEB_DRAFT_IMAGE_DIR = str(get_image_dir("web", draft=True))
ANDROID_DRAFT_IMAGE_DIR = str(get_image_dir("android", draft=True))
FLUTTER_DRAFT_IMAGE_DIR = str(get_image_dir("flutter", draft=True))

# 保留旧变量名，但它们现在代表当前 PLATFORM 对应的平台目录。
path = str(get_image_dir(CURRENT_PLATFORM))
test_path = str(get_image_dir(CURRENT_PLATFORM, draft=True))


# =====================================================================
# Swan (Flutter) 元素图片
# 2026-09-08 真机验证（aw-verify，serial c0614b6a，720x1600）全部通过，
# 已由 promote_image 转正到 image/flutter/，常量登记为正式路径。
# =====================================================================

# --- 首页 (swan_home_page) ---
SWAN_BOTTOM_PLAYER_BAR = image_path("swan_bottom_player_bar.png", platform="flutter")

# --- 我的 (swan_me_page) ---
SWAN_ME_FAMILY_MANAGE_ROW = image_path("swan_me_family_manage_row.png", platform="flutter")
SWAN_ME_FAVORITES_ROW = image_path("swan_me_favorites_row.png", platform="flutter")
SWAN_ME_DEVICE_MANAGE_ROW = image_path("swan_me_device_manage_row.png", platform="flutter")
SWAN_ME_SOUND_QUALITY_ROW = image_path("swan_me_sound_quality_row.png", platform="flutter")

# --- 家庭管理 (swan_family_manage_page) ---
SWAN_FAMILY_ADD_MEMBER_ICON = image_path("swan_family_add_member_icon.png", platform="flutter")

# --- SWAN收藏 (swan_favorites_page) ---
SWAN_FAV_FAMILY_GROUP_ROW = image_path("swan_fav_family_group_row.png", platform="flutter")
SWAN_FAV_MUSIC_GROUP_ROW = image_path("swan_fav_music_group_row.png", platform="flutter")
SWAN_FAV_ADD_PLAYLIST_BUTTON = image_path("swan_fav_add_playlist_button.png", platform="flutter")

# --- 音质设置弹层 (swan_sound_quality_page) ---
SWAN_SOUND_QUALITY_DONE_BUTTON = image_path("swan_sound_quality_done_button.png", platform="flutter")

# --- 验证码登录页 (swan_login_sms_page) ---
SWAN_LOGIN_PRIVACY_POLICY_LINK = image_path("swan_login_privacy_policy_link.png", platform="flutter")
SWAN_LOGIN_USAGE_POLICY_LINK = image_path("swan_login_usage_policy_link.png", platform="flutter")
SWAN_LOGIN_SUBMIT_BTN = image_path("swan_login_submit_btn.png", platform="flutter")

# --- 验证码输入页 (swan_login_code_page) ---
SWAN_LOGIN_CODE_FIELD_BOX = image_path("swan_login_code_field_box.png", platform="flutter")

# --- 播放页 (swan_player_page) ---
SWAN_PLAYER_PLAY_PAUSE_BTN = image_path("swan_player_play_pause_btn.png", platform="flutter")
SWAN_PLAYER_DISMISS_BTN = image_path("swan_player_dismiss_btn.png", platform="flutter")

# --- 设备页 (swan_device_page) ---
SWAN_DEVICE_ADD_BTN = image_path("swan_device_add_btn.png", platform="flutter")

# --- 平台页 (swan_platform_page) ---
SWAN_PLATFORM_NETEASE_ROW = image_path("swan_platform_netease_row.png", platform="flutter")


__all__ = [
    "ANDROID_DRAFT_IMAGE_DIR",
    "ANDROID_IMAGE_DIR",
    "FLUTTER_DRAFT_IMAGE_DIR",
    "FLUTTER_IMAGE_DIR",
    "CURRENT_PLATFORM",
    "DRAFT_IMAGE_ROOT",
    "FORMAL_IMAGE_ROOT",
    "SUPPORTED_PLATFORMS",
    "SWAN_BOTTOM_PLAYER_BAR",
    "SWAN_DEVICE_ADD_BTN",
    "SWAN_FAV_ADD_PLAYLIST_BUTTON",
    "SWAN_FAV_FAMILY_GROUP_ROW",
    "SWAN_FAV_MUSIC_GROUP_ROW",
    "SWAN_FAMILY_ADD_MEMBER_ICON",
    "SWAN_LOGIN_CODE_FIELD_BOX",
    "SWAN_LOGIN_PRIVACY_POLICY_LINK",
    "SWAN_LOGIN_SUBMIT_BTN",
    "SWAN_LOGIN_USAGE_POLICY_LINK",
    "SWAN_ME_DEVICE_MANAGE_ROW",
    "SWAN_ME_FAMILY_MANAGE_ROW",
    "SWAN_ME_FAVORITES_ROW",
    "SWAN_ME_SOUND_QUALITY_ROW",
    "SWAN_PLATFORM_NETEASE_ROW",
    "SWAN_PLAYER_DISMISS_BTN",
    "SWAN_PLAYER_PLAY_PAUSE_BTN",
    "SWAN_SOUND_QUALITY_DONE_BUTTON",
    "WEB_DRAFT_IMAGE_DIR",
    "WEB_IMAGE_DIR",
    "demote_image",
    "get_image_dir",
    "image_path",
    "normalize_platform",
    "path",
    "promote_image",
    "test_path",
]
