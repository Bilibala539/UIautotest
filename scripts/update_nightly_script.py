import paramiko

CRON_SCRIPT = r"""#!/bin/bash

WINDOWS_HOST="wb.menglingzhao02@10.219.191.200"
LOG_DIR="/var/www/html/reports/nightly-logs"
DATE=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/$DATE.log"
SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=60 -o BatchMode=yes"

mkdir -p "$LOG_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 触发 UIAutotestNightly 任务" | tee "$LOG_FILE"

# 触发 Task Scheduler 任务（在桌面 session 里运行）
ssh $SSH_OPTS "$WINDOWS_HOST" \
  "schtasks /run /tn UIAutotestNightly 2>&1" \
  >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 任务已触发，等待完成..." | tee -a "$LOG_FILE"

# 轮询任务状态，直到不再是 Running
MAX_WAIT=10800  # 最多等 3 小时
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
  sleep 30
  ELAPSED=$((ELAPSED + 30))

  STATUS=$(ssh $SSH_OPTS "$WINDOWS_HOST" \
    "schtasks /query /tn UIAutotestNightly /fo csv /nh 2>&1" | tr -d '\r')

  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 状态: $STATUS (已等待 ${ELAPSED}s)" >> "$LOG_FILE"

  # 不包含 Running 即为完成
  if echo "$STATUS" | grep -v "Running" | grep -q "UIAutotestNightly"; then
    break
  fi
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 测试完成，发送报告" | tee -a "$LOG_FILE"

ssh $SSH_OPTS "$WINDOWS_HOST" \
  "cd /d E:\\UIAutotest && python scripts\\send_nightly_report.py 2>&1" \
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
_, o, _ = ssh.exec_command("cat /var/www/html/reports/run_nightly.sh")
print(o.read().decode())
ssh.close()
print("服务器脚本已更新")
