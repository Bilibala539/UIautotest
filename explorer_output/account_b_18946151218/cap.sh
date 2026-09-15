#!/bin/bash
# cap.sh <name>  — dump + screencap into explorer_output/account_b_18946151218
export ANDROID_DEVICE_SERIAL=AKFDCP4718428516
A=/c/platform-tools/adb.exe
OUT=/e/uiautotest/explorer_output/account_b_18946151218
NAME="$1"
MSYS_NO_PATHCONV=1 $A shell "uiautomator dump /sdcard/cap.xml" >/dev/null 2>&1
sleep 0.3
MSYS_NO_PATHCONV=1 $A exec-out cat /sdcard/cap.xml > "$OUT/$NAME.xml"
MSYS_NO_PATHCONV=1 $A exec-out screencap -p > "$OUT/$NAME.png"
echo "saved $NAME.xml $(wc -c < "$OUT/$NAME.xml") bytes"
