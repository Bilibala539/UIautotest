# Laya 本地决策模型 POC

测试"文字用例是否靠谱"能否用 Laya（Convai Innovations 开源的 Jev 兼容决策模型）本地判定。
分支：`laya-poc`（独立于 master 开发线）。

## 目录

| 目录 | 内容 | 部署位置 |
|---|---|---|
| `platform-167/` | POC 脚本（用例抽取 + 三实验 + 诊断） | .167 `~/laya_poc/` |
| `platform-167/results/` | 实验数据（164 条用例 + 结果 CSV/JSON + 诊断日志） | 同上 |
| `judge-176/` | GPU 判定 HTTP 服务 | .176 `~/laya-judge/` |
| `leader/` | 两级 agent 编排：小领导章程 ×2 + 引导脚本 | 各机 `~/leader/LEADER.md` |

## POC 设计（防作弊是核心）

用例从平台库只读抽取（`extract.py` → `cases.json`，164 条文本用例，剥掉 `name:`/`domain:` 行防模型偷答案）：

- **EXP1 一致性**：真标题 vs 错配标题（sham = `cases[(i+7)%n]`），noul 判断"标题与内容是否同一场景"。真错配对天然构成 ground truth，**不用人工标注**。
- **EXP2 域分类**：25 条带 domain 标签的用例做 choice 分类。
- **EXP3 可验证性**：noul 判断"预期结果是否明确可观察"。

## 当前结论（诊断中，2026-09-22）

| 实验 | 结果 | 判读 |
|---|---|---|
| EXP1 一致性 | true mean=0.991 / sham mean=0.992，acc≈0.50（随机） | **失败**：noul 饱和 |
| EXP2 域分类 | exact=0.279（25 类随机≈0.04） | 显著高于随机但不可用 |
| EXP3 可验证性 | 全部 ≥0.5 | 饱和，无区分度 |

已排除假设：**不是**上下文溢出（max_len 1024/2048 结果逐位相同）；**不是**指令措辞（3 种 prompt 变体全饱和）。英文 checkpoint 对照 + 余弦基线对照进行中（`exp_diag3.py`）。

初步判断：multilingual 版（mmBERT-base）的 noul 头对中文长结构化文本的语义一致性无判别力——简单句可用（EN trivial TRUE=0.095 / FALSE=0.013），长用例体全部拉满到 ~0.99。

## GPU judge 服务（.176:8089）

- 架构：单实例 HTTP 服务，各测试机调 `POST /predict {"state","questions"}`，避免每台机器装 CUDA
- `judge_server.py`：stdlib ThreadingHTTPServer，token 鉴权（`X-Judge-Token`，token.txt 不入库），全局锁串行 predict，warmup 预热，`GET /health`
- `start.sh`：HF 镜像 + venv 启动；`laya-judge.service`：systemd 常驻
- 部署由 m176-leader 执行（176-001），硬边界：不碰 Jenkins
- RTX 4070 驱动 580.178.04 已装好（nouveau 抢占已修，黑名单已补）

## 两级 agent 编排

大领导（.229 主会话）派活 → 小领导（各机 tmux `leader` 会话里的常驻 claude）执行，可自起 teammate。任务进 `~/leader/inbox/<ts>.md`，报告出 `~/leader/outbox/<ts>.md`。章程见 `leader/LEADER-m*.md`：

- m167：平台库严格只读、不停任何服务、不改 /opt/uiautotest、不 apt
- m176：绝不碰 Jenkins 与 /opt/build-env、不重启机器，sudo 仅限 NVIDIA 驱动 / judge 单元 / 8089 防火墙
