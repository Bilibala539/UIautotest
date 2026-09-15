"""YAML 用例正式 schema 的加载与校验(① 数据层 loader)。

YAML 用例是文字用例与自动化脚本之间的**正式载体**:同一 case_id 下,
人类可读的步骤描述与机器可执行的 action 序列绑定存放。文件位置:
knowledge/swan/cases/driver/<module>/<CASE_ID>.yaml

Schema:
    case_id: POS-002          # 必填,与文字用例编号一致
    title: ...                # 必填,一句话用例名
    module: login             # 必填,所属模块
    priority: P0              # 可选
    source: ...               # 可选,来源(文字用例路径 / bug:SWAN-BUG-xxx)
    preconditions: [...]      # 可选,前置条件(人类可读;状态归一化由 driver 负责)
    steps:                    # 必填,顺序执行
      - action: <AW/业务方法名>   # 必填,必须在允许名单内
        args: {key: value}       # 可选,值为 "${VAR}" 时从运行上下文插值
        desc: 步骤说明           # 可选,文字步骤(人读)
        assert: true             # 可选,布尔型返回值是否断言(默认 true)
    expected: ...             # 可选,预期结果(人类可读)

插值:步骤 args 中 "${name}" 按运行上下文解析(phone=测试账号,
otp=实时验证码),其余从环境变量取;未定义的变量报错(不用例带病执行)。
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASE_DIR = PROJECT_ROOT / "knowledge" / "swan" / "cases" / "driver"

_REQUIRED_TOP = {"case_id", "title", "module", "steps"}
_KNOWN_TOP = {"case_id", "title", "module", "priority", "source", "preconditions", "steps", "expected"}
_KNOWN_STEP = {"action", "args", "desc", "assert"}
_PLACEHOLDER = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


class CaseLoadError(ValueError):
    """YAML 用例不符合 schema。"""


@dataclass
class YamlCase:
    case_id: str
    title: str
    module: str
    priority: str = ""
    source: str = ""
    preconditions: list = field(default_factory=list)
    steps: list = field(default_factory=list)
    expected: str = ""
    path: Path = None  # noqa: RUF100


def _validate_step(index: int, step: dict) -> dict:
    if not isinstance(step, dict):
        raise CaseLoadError(f"step[{index}] 必须是映射,得到 {type(step).__name__}")
    action = step.get("action")
    if not action or not isinstance(action, str):
        raise CaseLoadError(f"step[{index}].action 必填(非空字符串)")
    unknown = set(step) - _KNOWN_STEP
    if unknown:
        raise CaseLoadError(f"step[{index}] 含未知字段: {sorted(unknown)}(允许 {sorted(_KNOWN_STEP)})")
    args = step.get("args", {})
    if not isinstance(args, dict):
        raise CaseLoadError(f"step[{index}].args 必须是映射")
    assert_flag = step.get("assert", True)
    if not isinstance(assert_flag, bool):
        raise CaseLoadError(f"step[{index}].assert 必须是布尔值")
    return {"action": action, "args": args, "desc": str(step.get("desc", "")), "assert": assert_flag}


def load_case(path: str | Path) -> YamlCase:
    path = Path(path)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise CaseLoadError(f"{path.name} YAML 解析失败: {error}") from error
    if not isinstance(raw, dict):
        raise CaseLoadError(f"{path.name} 顶层必须是映射")
    missing = _REQUIRED_TOP - set(raw)
    if missing:
        raise CaseLoadError(f"{path.name} 缺少必填字段: {sorted(missing)}")
    unknown = set(raw) - _KNOWN_TOP
    if unknown:
        raise CaseLoadError(f"{path.name} 含未知字段: {sorted(unknown)}(允许 {sorted(_KNOWN_TOP)})")
    if not isinstance(raw["steps"], list) or not raw["steps"]:
        raise CaseLoadError(f"{path.name}.steps 必须是非空列表")
    steps = [_validate_step(i, step) for i, step in enumerate(raw["steps"], 1)]
    return YamlCase(
        case_id=str(raw["case_id"]),
        title=str(raw["title"]),
        module=str(raw["module"]),
        priority=str(raw.get("priority", "")),
        source=str(raw.get("source", "")),
        preconditions=list(raw.get("preconditions", [])),
        steps=steps,
        expected=str(raw.get("expected", "")),
        path=path,
    )


def discover_cases(case_dir: str | Path = DEFAULT_CASE_DIR) -> list[Path]:
    """发现所有 YAML 用例文件(按 case_id 排序,保证执行顺序稳定)。"""
    case_dir = Path(case_dir)
    if not case_dir.exists():
        return []
    files = sorted(case_dir.rglob("*.yaml"), key=lambda p: p.name)
    return [p for p in files if not p.name.startswith("_")]


def interpolate(value, context: dict):
    """递归插值:"${name}" 按 context → 环境变量顺序解析;未定义报错。"""
    if isinstance(value, str):
        def _sub(match: re.Match) -> str:
            name = match.group(1)
            if name in context:
                return str(context[name])
            if name in os.environ:
                return os.environ[name]
            raise CaseLoadError(f"插值变量 ${{{name}}} 未定义(运行上下文与环境变量中均无)")
        return _PLACEHOLDER.sub(_sub, value)
    if isinstance(value, dict):
        return {k: interpolate(v, context) for k, v in value.items()}
    if isinstance(value, list):
        return [interpolate(v, context) for v in value]
    return value
