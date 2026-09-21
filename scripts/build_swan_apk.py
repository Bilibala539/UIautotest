"""Swan 打包脚本(源码检出 → flutter 构建 → 平台登记)。

跑在构建机(176,Ubuntu;Windows 本机开发也可直跑),依赖构建环境
(JDK/Android SDK/Flutter,路径可用 .env.local 同名键覆盖)和 .env.local 里的
GitLab 机器人账号。构建根目录可用环境变量 SWAN_BUILD_ROOT 覆盖,
缺省按系统分流:Windows=E:\\swan-build / Linux=/opt/swan-build。
用法:
  python scripts/build_swan_apk.py                    # 构建 dev 分支并登记
  python scripts/build_swan_apk.py --branch master    # 指定分支(dev/master/harmony)
  python scripts/build_swan_apk.py --commit abc1234   # 指定 commit
  python scripts/build_swan_apk.py --skip-build       # 跳过构建,直接登记已有产物
  python scripts/build_swan_apk.py --keep-src         # 构建后不删源码
  python scripts/build_swan_apk.py --server-type formal  # 正式服包=--release(Release 锁正式服);默认 test=--profile(AOT 且默认连测试服,关于页可切服)
  python scripts/build_swan_apk.py --notes "%E5%8E%8B%E6%B5%8B"  # 登记备注(URL 编码,平台 /api/builds 触发时 quote 传入)
app 的 pubspec.yaml 以相对路径引用核心仓,检出时会一并 clone 核心仓到源码同级目录。
权限尚未生效时可用 --repo-url/--core-repo-url 指向本地裸仓验证检出逻辑(不构建不登记)。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# 构建根目录:SWAN_BUILD_ROOT 环境变量优先;缺省按系统分流
# (Windows 本机开发保持 E:\swan-build,176 构建机为 /opt/swan-build)。
# 其余固定路径约定(JAVA_HOME/ANDROID_HOME/FLUTTER_HOME)可用 .env.local 同名键覆盖
ENV_FILE = Path(__file__).resolve().parent.parent / ".env.local"
BUILD_ROOT = Path(os.environ.get(
    "SWAN_BUILD_ROOT", r"E:\swan-build" if os.name == "nt" else "/opt/swan-build"))
SRC_DIR = BUILD_ROOT / "src"
LOG_DIR = BUILD_ROOT / "logs"
PLATFORM_URL = os.environ.get("DASHBOARD_URL", "http://127.0.0.1:8080").rstrip("/")
REPO_URL = "https://git.hivi.com/swan-app/swan-audio/hivi-network-flutterapp.git"
# app 的 pubspec.yaml 以 `path: ../hivi_network_flutter_core` 相对路径引用核心仓,
# 核心仓必须 clone 到 SRC_DIR 同级且目录名与相对路径精确一致
CORE_REPO_URL = "https://git.hivi.com/swan-app/swan-audio/hivi_network_flutter_core.git"
CORE_SRC_DIR = SRC_DIR.parent / "hivi_network_flutter_core"

DEFAULTS = {
    "JAVA_HOME": r"C:\build-env\jdk-17",
    "ANDROID_HOME": r"C:\build-env\android",
    "FLUTTER_HOME": r"C:\build-env\flutter",
    "FLUTTER_STORAGE_BASE_URL": "https://storage.flutter-io.cn",
    "PUB_HOSTED_URL": "https://pub.flutter-io.cn",
}


def load_env(path: Path) -> dict[str, str]:
    """解析 .env.local,格式 KEY=VALUE,忽略 BOM/注释/空行,不回显任何值。"""
    env: dict[str, str] = {}
    if not path.is_file():
        return env
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key:
            env[key] = value.strip()
    return env


def redact(text: str, secrets: list[str]) -> str:
    """日志脱敏:密码字面量替换为 ***,带凭据的 URL 归一为 git.hivi.com/...。"""
    for secret in secrets:
        if secret:
            text = text.replace(secret, "***")
    # https://user:pwd@host/... → git.hivi.com/...(凭据部分整体抹掉)
    return re.sub(r"(?i)https?://[^/\s@]+@git\.hivi\.com", "git.hivi.com", text)


def run(cmd: list[str], cwd: Path, log, secrets: list[str], env: dict[str, str] | None = None) -> None:
    """执行命令,输出经脱敏后写入日志;失败抛 RuntimeError。env 显式传入构建环境
    (JAVA_HOME/ANDROID_HOME 等)——Jenkins SYSTEM 会话缺这些变量,不传则 flutter 找不到 SDK。"""
    printable = [redact(part, secrets) if ":" in part or "@" in part else part for part in cmd]
    log.write(f"$ {subprocess.list2cmdline(printable)}\n")
    log.flush()
    result = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=env,
    )
    output = redact((result.stdout or "") + (result.stderr or ""), secrets)
    log.write(output)
    if result.returncode != 0:
        raise RuntimeError(f"命令失败 exit={result.returncode}: {printable[0]} …(详见日志)")


def git_out(src: Path, *args: str) -> str:
    """执行只读 git 命令并返回 stdout(可能抛错,由调用方处理)。"""
    result = subprocess.run(
        ["git", "-C", str(src), *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败: {result.stderr.strip()}")
    return result.stdout.strip()


def repo_healthy(src: Path) -> bool:
    """git 自证仓库可用:.git/HEAD 存在 + rev-parse 成功且输出 true 才算健康。
    .git 残骸(目录在但 HEAD 等核心文件已丢,build #8)会骗过目录存在性检查,
    骗不过 git 自己;git 不可用(FileNotFoundError)也按损坏处理。"""
    if not (src / ".git" / "HEAD").is_file():
        return False
    try:
        result = subprocess.run(
            ["git", "-C", str(src), "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0 and result.stdout.strip() == "true"


def ensure_src(src: Path, url: str, secrets: list[str], log) -> None:
    """确保源码目录存在:没有则 clone;已有则 git 自证健康后 fetch+prune;目录在但
    自证失败(.git 残骸/半删除残留)清掉重 clone(档案坑 14)。URL 不落日志明文。"""
    src.parent.mkdir(parents=True, exist_ok=True)
    if not src.is_dir():
        log.write("源码目录不存在,执行 clone\n")
        run(["git", "clone", url, str(src)], src.parent, log, secrets)
        return
    if repo_healthy(src):
        log.write("源码目录已存在,执行 fetch --all --prune\n")
        run(["git", "-C", str(src), "fetch", "--all", "--prune"], src, log, secrets)
        return
    # 残留/损坏目录直接 clone 会报"已存在且非空"(build #7/#8 连锁失败根源),先清掉
    log.write("源码目录损坏(.git 残骸或缺少仓库元数据),清除后重新 clone\n")
    force_rmtree(src)
    run(["git", "clone", url, str(src)], src.parent, log, secrets)


def checkout_target(src: Path, branch: str, commit: str, secrets: list[str], log) -> str:
    """检出目标分支或 commit,返回完整 commit hash。分支做 hard reset 对齐远端。"""
    if commit:
        log.write(f"checkout commit {commit}\n")
        run(["git", "-C", str(src), "checkout", "--force", commit], src, log, secrets)
    else:
        # 分支:优先跟踪 origin/<branch>(clone 后远端引用已就绪)
        log.write(f"checkout branch {branch}\n")
        run(["git", "-C", str(src), "checkout", "--force", "-B", branch, f"origin/{branch}"],
            src, log, secrets)
        run(["git", "-C", str(src), "reset", "--hard", f"origin/{branch}"], src, log, secrets)
    return git_out(src, "rev-parse", "HEAD")


def build_env(creds: dict[str, str]) -> dict[str, str]:
    """合并系统环境 + .env.local 覆盖 + 固定默认值,得到构建子进程环境。"""
    env = dict(os.environ)
    for key, value in DEFAULTS.items():
        env[key] = creds.get(key, value)
    flutter_bin = str(Path(env["FLUTTER_HOME"]) / "bin")
    env["PATH"] = flutter_bin + os.pathsep + str(Path(env["JAVA_HOME"]) / "bin") \
        + os.pathsep + env["PATH"]
    return env


def rotate_logs(keep: int = 20) -> None:
    """只保留最近 keep 个构建日志。"""
    logs = sorted(LOG_DIR.glob("build_*.log"))
    for old in logs[:-keep]:
        old.unlink(missing_ok=True)


def force_rmtree(path: Path) -> None:
    """Windows 下删除目录树的兜底:git objects 只读需解除只读重删;构建产物里还有
    超长路径(常规 API 删不动,用 \\\\?\\ 扩展前缀重试)和"文件在遍历与回调之间被
    杀软等并发删掉"的竞态(存在性判断放过);整体失败隔 1s 重试一次防杀软短暂占用。
    两次仍失败则抛出,由调用方决定是否容忍(清理段 best-effort,检出自愈则致命)。
    """
    def on_error(func, target, _exc_info):
        # 用 \\?\ 前缀探存在性:常规 API 对超长路径 stat 会误报"不存在",前缀形式总能正确解析
        marked = "\\\\?\\" + str(target)
        if not os.path.exists(marked):
            return  # 文件已消失(build #6 的删除竞态),放过即可
        os.chmod(marked, stat.S_IWRITE)
        try:
            func(target)
        except OSError:
            # 常规删除失败(超长路径/残留占用):用 \\?\ 扩展前缀重试一次
            if os.path.isdir(marked):
                shutil.rmtree(marked, ignore_errors=True)
            else:
                os.remove(marked)
    for attempt in range(2):
        try:
            shutil.rmtree(path, onerror=on_error)
            return
        except OSError:
            if attempt == 0:
                time.sleep(1)  # 第一次失败:可能杀软/索引服务短暂占用,稍候重试
            else:
                raise


def register_apk(payload: dict[str, str]) -> dict[str, str]:
    """POST 平台 /api/apks 登记,返回服务端响应。"""
    request = urllib.request.Request(
        f"{PLATFORM_URL}/api/apks",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def upload_archive(archive: Path, apk_id: str) -> dict[str, object]:
    """把 APK 字节推给平台归档(POST /api/apks/<apk_id>/file)。

    跨机拓扑下平台读不到构建机磁盘,扫码下载回源 output/apks/<apk_id>.apk,
    登记成功后必须完成这一步,平台侧下载/二维码才真正可用。
    """
    request = urllib.request.Request(
        f"{PLATFORM_URL}/api/apks/{urllib.parse.quote(apk_id, safe='')}/file",
        data=archive.read_bytes(),
        headers={"Content-Type": "application/octet-stream"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Swan 自动打包并登记进平台")
    parser.add_argument("--branch", default="dev", help="构建分支(dev/master/harmony,默认 dev)")
    parser.add_argument("--commit", default="", help="构建指定 commit(优先于分支)")
    parser.add_argument("--repo-url", default=REPO_URL, help="app 仓地址(自测可指本地裸仓)")
    parser.add_argument("--core-repo-url", default=CORE_REPO_URL,
                        help="核心仓地址(默认 hivi_network_flutter_core,自测可指本地裸仓)")
    parser.add_argument("--skip-build", action="store_true", help="跳过构建,直接登记已有产物(调试)")
    parser.add_argument("--only-checkout", action="store_true", help="只验证检出流程,不构建不登记(自测)")
    parser.add_argument("--keep-src", action="store_true", help="构建完成后不删除源码目录")
    parser.add_argument("--server-type", choices=["formal", "test"], default="test",
                        help="服务器类型(formal=正式服/test=测试服,默认 test)")
    parser.add_argument("--notes", default="",
                        help="登记备注(URL 编码字符串,与平台 /api/builds 的 quote 行为对齐)")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    creds = load_env(ENV_FILE)
    # DASHBOARD_URL 解析优先级:进程环境变量 > .env.local 同名键 > 模块默认(127.0.0.1:8080)。
    # 176 构建机上平台在 167,.env.local 是登记地址的权威来源(Jenkins agent 会话无该环境变量)。
    global PLATFORM_URL
    PLATFORM_URL = os.environ.get("DASHBOARD_URL",
                                  creds.get("DASHBOARD_URL", PLATFORM_URL)).rstrip("/")
    user = creds.get("GITLAB_BOT_USER", "")
    pwd = creds.get("GITLAB_BOT_PASSWORD", "")
    if not user or not pwd:
        print("缺少 GITLAB_BOT_USER / GITLAB_BOT_PASSWORD,无法拼出拉取凭据")
        return 1
    secrets = [pwd]
    # 凭据只进 git URL,不进任何日志/命令行回显;app 与 core 两仓同一 GitLab 机器人账号
    authed_url = f"https://{user}:{pwd}@git.hivi.com/swan-app/swan-audio/hivi-network-flutterapp.git"
    authed_core_url = f"https://{user}:{pwd}@git.hivi.com/swan-app/swan-audio/hivi_network_flutter_core.git"
    if args.repo_url != REPO_URL:  # 本地裸仓调试路径,无需凭据
        authed_url = args.repo_url
    if args.core_repo_url != CORE_REPO_URL:
        authed_core_url = args.core_repo_url
    # 平台 /api/builds 触发时 notes 是 URL 编码串(规避 Windows 批处理编码坑),此处解码;
    # 命令行直跑也建议传 URL 编码值,与平台行为一致
    user_notes = urllib.parse.unquote(args.notes)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S") + f"_{os.getpid()}"
    log_path = LOG_DIR / f"build_{stamp}.log"
    log = log_path.open("w", encoding="utf-8")
    started = time.monotonic()
    build_time = ""  # 构建完成时间,--skip-build 时回落到产物文件 mtime
    # server_type 决定构建模式:核心仓 ServerEnvironmentManager 在 Release 包锁死正式服且
    # dart-define 无效;profile 包 AOT 且非 Release 默认连 staging 测试服、关于页可切服(档案坑 13)
    build_mode = "profile" if args.server_type == "test" else "release"

    def echo(msg: str) -> None:
        log.write(msg + "\n")
        print(msg)

    try:
        if args.skip_build:
            echo("--skip-build:跳过源码与构建,直接登记已有产物")
            # 核心仓缺失也要补 clone(pubspec 相对路径引用,缺失会导致后续 flutter pub get 失败)
            if not (CORE_SRC_DIR / ".git").is_dir():
                echo("核心仓缺失,补 clone")
                ensure_src(CORE_SRC_DIR, authed_core_url, secrets, log)
            src = SRC_DIR
        else:
            echo(f"== 步骤 1/3 检出源码({log_path}) ==")
            ensure_src(SRC_DIR, authed_url, secrets, log)
            checkout_target(SRC_DIR, args.branch, args.commit, secrets, log)
            commit_hash = git_out(SRC_DIR, "rev-parse", "HEAD")
            echo(f"检出完成 commit={commit_hash}")
            # 核心仓:默认与 app 同分支;--commit 只作用于 app 仓
            ensure_src(CORE_SRC_DIR, authed_core_url, secrets, log)
            checkout_target(CORE_SRC_DIR, args.branch, "", secrets, log)
            if args.only_checkout:
                echo("--only-checkout:检出验证结束,不构建不登记")
                log.close()
                rotate_logs()
                return 0

            echo(f"== 步骤 2/3 flutter build apk --{build_mode} ==")
            env = build_env(creds)
            flutter = str(Path(env["FLUTTER_HOME"]) / "bin"
                          / ("flutter.bat" if os.name == "nt" else "flutter"))
            build_start = time.monotonic()
            run([flutter, "build", "apk", f"--{build_mode}"], SRC_DIR, log, secrets, env=env)
            build_time = time.strftime("%Y-%m-%d %H:%M:%S")
            echo(f"构建耗时 {time.monotonic() - build_start:.0f}s")
    except (RuntimeError, OSError) as error:
        echo(f"失败:{error}")
        log.write(f"失败:{error}\n")
        log.close()
        rotate_logs()
        return 1

    # ---- 产物登记 ----
    # APK 归档到 BUILD_ROOT/apks:源码目录默认会被清理,登记的 file_path 必须指向持久位置
    apk_src = SRC_DIR / "build" / "app" / "outputs" / "flutter-apk" / f"app-{build_mode}.apk"
    if not apk_src.is_file():
        echo(f"产物不存在:{apk_src}")
        log.close()
        rotate_logs()
        return 1
    if not build_time:
        # --skip-build 没有本次构建,取产物文件修改时间作为构建完成时间
        build_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(apk_src.stat().st_mtime))
    archive_dir = BUILD_ROOT / "apks"
    short = git_out(SRC_DIR, "rev-parse", "--short", "HEAD") if (SRC_DIR / ".git").is_dir() else "unknown"
    archive_dir.mkdir(parents=True, exist_ok=True)
    # apk_id 带 server_type 段:同分支同 commit 同日的 formal/test 两包不互相覆盖
    apk_id = f"swan-{args.branch}-{short}-{time.strftime('%Y%m%d')}-{args.server_type}"
    apk = archive_dir / f"{apk_id}.apk"
    shutil.copy2(apk_src, apk)
    file_hash = hashlib.sha256(apk.read_bytes()).hexdigest()
    elapsed = int(time.monotonic() - started)
    payload = {
        "apk_id": apk_id,
        "app_version": "",
        "branch": args.branch,
        "commit_hash": short,
        "flavor": build_mode,
        "source": "auto-build",
        "server_type": args.server_type,
        "build_time": build_time,
        # Jenkins 构建身份(Jenkins job 内跑时环境变量天然存在;本地直跑为空串,
        # 平台按空串存,供包管理页跳转 Jenkins 日志用)
        "jenkins_job": os.environ.get("JOB_NAME", ""),
        "jenkins_build": os.environ.get("BUILD_NUMBER", ""),
        "file_path": str(apk),
        "file_hash": file_hash,
        # notes = 用户备注(如有,置前) + 自动信息(分支/commit/构建模式/构建耗时)
        "notes": (f"{user_notes}; " if user_notes else "")
                 + f"branch={args.branch} commit={short} mode={build_mode} 构建耗时={elapsed}s",
    }
    echo(f"== 步骤 3/3 登记平台({PLATFORM_URL}/api/apks server_type={args.server_type})==")
    try:
        result = register_apk(payload)
        echo(f"登记成功 apk_id={result.get('apk_id')} sha256={file_hash[:12]}… server_type={args.server_type}")
    except (urllib.error.URLError, OSError, ValueError) as error:
        echo(f"登记失败:{error}(产物仍在 {apk})")
        log.close()
        rotate_logs()
        return 1

    # 登记成功=平台可下载:归档上传是登记的必要后半步,失败按登记失败同一口径处理
    echo(f"== 归档产物到平台({PLATFORM_URL}/api/apks/{apk_id}/file)==")
    upload_error = ""
    for attempt in (1, 2):
        try:
            uploaded = upload_archive(apk, apk_id)
            echo(f"归档成功 bytes={uploaded.get('bytes')} → {uploaded.get('stored')}")
            break
        except (urllib.error.URLError, OSError, ValueError) as error:
            upload_error = str(error)
            echo(f"归档失败(第 {attempt} 次):{upload_error}")
            time.sleep(2)
    else:
        echo(f"归档失败:{upload_error}(登记行已存在但平台无法下载,请重跑或手工上传;产物仍在 {apk})")
        log.close()
        rotate_logs()
        return 1

    if not args.keep_src and not args.skip_build:
        echo("清理源码目录(未指定 --keep-src)")
        # 构建与登记均已成功,清理只是 best-effort:任何清理异常都不得让本次构建标 FAILURE
        # (build #6 即清理崩溃打穿 try 块外,Jenkins 误标 FAILURE)
        try:
            force_rmtree(SRC_DIR)
            force_rmtree(CORE_SRC_DIR)
        except Exception as error:
            echo(f"清理失败(不影响产物与登记):{error}")
    log.close()
    rotate_logs()
    return 0


if __name__ == "__main__":
    sys.exit(main())
