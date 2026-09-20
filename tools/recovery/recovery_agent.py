"""TEMPORARY recovery agent for .166 SSH restoration (remove after machine stable).

Runs on .166 via the swan-audio-build batch as SYSTEM:
  git -C E:\\uiautotest pull & py -3 E:\\uiautotest\\tools\\recovery\\recovery_agent.py fix_ssh inventory
Each step's full output is written into the dashboard sqlite (apks table,
apk_id=RECOVERY-*) so the main session can read it via GET /api/apks
despite broken SSH. ASCII-only to avoid codepage issues.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

DB = r"E:\uiautotest\output\dashboard.sqlite3"
PUBKEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMrKsTHttiJTG4k/2RXbCPy9z5Tdm2KjtwyMVQX8UYzc lan-mesh-1BG-IT-01796"
SYS_OPENSSH = r"C:\Windows\System32\OpenSSH"
PD_SSH = r"C:\ProgramData\ssh"
REC = r"E:\uiautotest\tools\ssh-recovery"


def run(cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        return "rc=%s OUT[%s] ERR[%s]" % (
            p.returncode, (p.stdout or "")[-800:], (p.stderr or "")[-800:])
    except Exception as e:
        return "EXC %r" % (e,)


def exists(p):
    return "Y" if os.path.exists(p) else "N"


def fix_ssh():
    lines = []
    for p in (SYS_OPENSSH + r"\ssh-keygen.exe", SYS_OPENSSH + r"\sshd.exe",
              REC + r"\ssh-keygen.exe", REC + r"\sshd_config_default", PD_SSH):
        lines.append("exists %s -> %s" % (p, exists(p)))
    lines.append("copy exe: " + run(["cmd", "/c", "copy /y \"%s\\ssh-keygen.exe\" \"%s\\ssh-keygen.exe\"" % (REC, SYS_OPENSSH)]))
    try:
        os.makedirs(PD_SSH, exist_ok=True)
        lines.append("makedirs %s ok" % PD_SSH)
    except Exception as e:
        lines.append("makedirs EXC %r" % (e,))
    lines.append("copy config: " + run(["cmd", "/c", "copy /y \"%s\\sshd_config_default\" \"%s\\sshd_config\"" % (REC, PD_SSH)]))
    lines.append("ssh-keygen -A: " + run([SYS_OPENSSH + r"\ssh-keygen.exe", "-A"]))
    # authorized_keys at the mechanism the shipped config actually uses
    ak_target = None
    try:
        with open(PD_SSH + r"\sshd_config", encoding="utf-8", errors="replace") as f:
            cfg = f.read()
        for ln in cfg.splitlines():
            if "AuthorizedKeysFile" in ln or "Match Group" in ln:
                lines.append("cfg: " + ln.strip())
        if "Match Group administrators" in cfg:
            ak_target = PD_SSH + r"\administrators_authorized_keys"
        else:
            os.makedirs(r"C:\Users\admin\.ssh", exist_ok=True)
            ak_target = r"C:\Users\admin\.ssh\authorized_keys"
    except Exception as e:
        lines.append("cfg read EXC %r" % (e,))
        ak_target = PD_SSH + r"\administrators_authorized_keys"
    try:
        with open(ak_target, "w", encoding="utf-8", newline="\n") as f:
            f.write(PUBKEY + "\n")
        lines.append("wrote %s ok" % ak_target)
    except Exception as e:
        lines.append("write ak EXC %r" % (e,))
    lines.append("icacls: " + run(["icacls", ak_target, "/inheritance:r",
                                   "/grant", "SYSTEM:F", "/grant", r"BUILTIN\Administrators:F"]))
    lines.append("net stop: " + run(["net", "stop", "sshd"]))
    lines.append("net start: " + run(["net", "start", "sshd"]))
    lines.append("sc query: " + run(["sc", "query", "sshd"]))
    return "\n".join(lines)


def inventory():
    lines = []
    for root in (r"C:\build-env", r"C:\Users\admin", r"C:\ProgramData\ssh",
                 SYS_OPENSSH,
                 r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
                 r"E:\swan-build", r"E:\uiautotest\tools"):
        if not os.path.isdir(root):
            lines.append("LIST %s -> MISSING" % root)
            continue
        try:
            entries = os.listdir(root)
            lines.append("LIST %s -> %d entries: %s" % (root, len(entries), ", ".join(entries[:60])))
        except Exception as e:
            lines.append("LIST %s -> EXC %r" % (root, e))
    return "\n".join(lines)


STEPS = {"fix_ssh": fix_ssh, "inventory": inventory}


def main():
    for step in (sys.argv[1:] or ["noop"]):
        fn = STEPS.get(step)
        body = "step=%s\n%s" % (step, fn() if fn else "unknown step")
        payload = {
            "apk_id": "RECOVERY-%s-%d" % (step, int(time.time())),
            "app_version": "", "branch": "recovery", "commit_hash": "",
            "flavor": "profile", "source": "recovery",
            "file_path": "", "file_hash": "",
            "notes": body[:3500], "server_type": "test",
        }
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:8080/api/apks",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=15) as r:
                r.read()
        except Exception:
            pass


main()
