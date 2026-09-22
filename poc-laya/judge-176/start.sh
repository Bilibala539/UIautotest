#!/bin/bash
cd "$(dirname "$0")"
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_DISABLE_XET=1
exec ./venv/bin/python judge_server.py
