# ShowUI-2B Windows 部署指南（CUDA GPU 版）

> 在 Windows 开发机上搭建 ShowUI-2B 多模态 UI 元素定位环境。独立 venv，不影响项目主环境。

---

## 前置条件

- Windows 10/11
- NVIDIA GPU（支持 CUDA，显存建议 ≥ 6GB）
- NVIDIA 驱动已安装（`nvidia-smi` 可正常输出）
- Python 3.12 已安装（可用 pyenv-win 或官方安装包）
- Git + Git LFS（`git lfs install` 已执行）

## Step 1: 确认 Python 3.12

```powershell
# 若用 pyenv-win
pyenv install 3.12.9
pyenv shell 3.12.9
python --version
# Python 3.12.9

# 若直接安装，确认路径
where python3.12
# 或 where python
```

## Step 2: 创建独立 venv

在项目根目录下创建 `.venv-showui`，不污染项目主环境（Python 3.9）。

```powershell
cd E:\UIAutotest
python3.12 -m venv .venv-showui
# 或（取决于 Python 3.12 的可执行文件名）
# "C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe" -m venv .venv-showui
```

## Step 3: 安装依赖

```powershell
# 激活 venv
.venv-showui\Scripts\activate

# 安装 PyTorch CUDA 版（根据你的 CUDA 版本选择）
# CUDA 12.1:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# CUDA 11.8:
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 安装 ShowUI 依赖
pip install "numpy<2"
pip install "transformers>=4.44,<4.47" accelerate qwen-vl-utils Pillow

# 退出 venv
deactivate
```

## Step 4: 下载模型

约 4.4GB，推荐 ModelScope 国内 CDN。

```powershell
# 使用 Git LFS 克隆
git lfs install
git clone --depth 1 https://www.modelscope.cn/AI-ModelScope/ShowUI-2B.git "%USERPROFILE%\.cache\huggingface\hub\models--showlab--ShowUI-2B"
```

或手动下载后放到 `~/.cache/huggingface/hub/models--showlab--ShowUI-2B/` 目录。

## Step 5: 验证安装

```powershell
.venv-showui\Scripts\python.exe -c "import torch; print('CUDA:', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

应输出类似：`CUDA: True NVIDIA GeForce RTX 3060`

```powershell
.venv-showui\Scripts\python.exe -c "from transformers import Qwen2VLForConditionalGeneration; print('transformers OK')"
```

## Step 6: 端到端验证

确保有一张 540×960 的测试截图，然后：

```powershell
.venv-showui\Scripts\python.exe utils\showui_agent.py locate E:\UIAutotest\output\screenshots\test.png "搜索按钮"
```

应输出类似：
```json
{"status": "ok", "center": [270, 85], "bbox": [240, 55, 300, 115], "confidence": 0.9, "raw_output": "[0.50, 0.09]", "inference_time_s": 3.2, "device": "cuda"}
```

---

## 目录结构

```
E:\UIAutotest\
├── .venv-showui\                          # ShowUI 专用 venv（Python 3.12 + CUDA）
├── utils\
│   └── showui_agent.py                    # 定位脚本（本项目代码）
└── %USERPROFILE%\.cache\huggingface\hub\
    └── models--showlab--ShowUI-2B\        # 模型权重 ~4.4GB
```

## 性能参考

| 硬件 | 推理耗时/次 | 说明 |
|------|-----------|------|
| GTX 1660 Ti (6GB VRAM) | ~90-95s | 当前开发机实测，主要耗时在图像 prefill |
| RTX 3060 (12GB VRAM) | ~15-25s（预估） | Ampere 架构 + 充足显存 |
| RTX 4070+ | ~5-10s（预估） | Ada Lovelace 架构 |
| CPU fallback | ~120-150s | 不推荐日常使用 |

> **实测结论**：GTX 1660 Ti 每次定位约 90 秒。对于批量元素截取（无人值守），10 个元素 ≈ 15 分钟，仍优于手工流程。
> 若需更快速度，建议升级到 RTX 3060+ 或使用远程 GPU 服务器。

---

## 注意事项

1. `.venv-showui` 已加入 `.gitignore`，不提交到仓库
2. 模型缓存在用户目录下（`~/.cache/`），跟随系统用户
3. 项目主环境（Python 3.9 venv）与 ShowUI 环境完全隔离，互不影响
4. aw-element agent 通过 `Bash` 工具调用 `.venv-showui\Scripts\python.exe utils/showui_agent.py`，无需在主环境中 import

## 故障排查

| 症状 | 原因 | 解决 |
|------|------|------|
| `torch.cuda.is_available()` 返回 False | CUDA 版本不匹配 | 确认 `nvidia-smi` 显示的 CUDA 版本，选对应的 torch 包 |
| OOM（显存不足） | GPU VRAM < 5GB | 改用 `torch_dtype=torch.float32` + CPU（慢但能跑）|
| `ModuleNotFoundError: qwen_vl_utils` | 漏装依赖 | `pip install qwen-vl-utils` |
| 模型加载报 `safetensors` 错误 | Git LFS 未正确拉取大文件 | 删除模型目录，重新 `git lfs clone` |
