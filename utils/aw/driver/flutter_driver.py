"""Flutter application driver backed by Android ADB."""
from __future__ import annotations

from utils.aw.driver.android_driver import AndroidAdbDriver


class FlutterAndroidDriver(AndroidAdbDriver):
    """Use the Android transport while keeping Flutter assets isolated."""

    @property
    def platform_name(self) -> str:
        return "flutter"
