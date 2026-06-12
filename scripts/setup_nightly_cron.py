import paramiko

CRON_SCRIPT = """\
#!/bin/bash
set -e

WINDOWS_HOST="wb.menglingzhao02@10.219.191.200"
LOG_DIR="/var/www/html/reports/nightly-logs"
DATE=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/$DATE.log"

mkdir -p "$LOG_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Start nightly test" | tee "$LOG_FILE"

ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 "$WINDOWS_HOST" \\
  "cd /d E:\\\\UIAutotest && python run_parallel.py -n 3 >> E:\\\\UIAutotest\\\\nightly.log 2>&1" \\
  >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tests done, sending report" | tee -a "$LOG_FILE"

ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 "$WINDOWS_HOST" \\
  "cd /d E:\\\\UIAutotest && python scripts\\\\send_nightly_report.py" \\
  >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] All done" | tee -a "$LOG_FILE"
"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("10.220.28.125", username="popoqa91", password="123456", timeout=15)

sftp = ssh.open_sftp()
with sftp.open("/var/www/html/reports/run_nightly.sh", "w") as f:
    f.write(CRON_SCRIPT)
sftp.close()

ssh.exec_command("chmod +x /var/www/html/reports/run_nightly.sh")

# 注册 cron（每天凌晨 01:00）
cron_line = "0 1 * * * /var/www/html/reports/run_nightly.sh"
stdin, stdout, stderr = ssh.exec_command(
    f"(crontab -l 2>/dev/null | grep -v run_nightly; echo '{cron_line}') | crontab -"
)
stdout.channel.recv_exit_status()

stdin2, stdout2, _ = ssh.exec_command("crontab -l")
print("当前 crontab:")
print(stdout2.read().decode())

ssh.close()
print("服务器端配置完成")
