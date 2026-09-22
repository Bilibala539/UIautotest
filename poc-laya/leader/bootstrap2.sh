#!/bin/bash
# usage: bootstrap2.sh <LEADER.md file> — synchronized claude TUI bootstrap in tmux
set -e
mkdir -p ~/leader/inbox ~/leader/outbox
cp "$1" ~/leader/LEADER.md
tmux kill-session -t leader 2>/dev/null || true
tmux new-session -d -s leader -n main
tmux send-keys -t leader "cd ~ && claude" Enter
pane() { tmux capture-pane -t leader -p 2>/dev/null; }

# wait for trust dialog
for i in $(seq 1 40); do
  pane | grep -q "trust this folder" && break
  sleep 1
done
if pane | grep -q "trust this folder"; then
  tmux send-keys -t leader Up; sleep 1; tmux send-keys -t leader Enter
  echo "TRUST_CONFIRMED"
else
  echo "NO_TRUST_DIALOG"; exit 1
fi

# wait for TUI ready (bypass permissions footer appears, dialog gone)
for i in $(seq 1 60); do
  if ! pane | grep -q "trust this folder" && pane | grep -q "bypass"; then break; fi
  sleep 1
done
pane | grep -q "bypass" || { echo "TUI_NOT_READY"; exit 1; }
echo "TUI_READY"

tmux send-keys -t leader -l "Read ~/leader/LEADER.md and follow it. You are this machine small leader. Reply with [LEADER-READY] plus one line stating your machine role."
sleep 1
tmux send-keys -t leader Enter

# wait for ready reply
for i in $(seq 1 120); do
  pane | grep -q "LEADER-READY" && { echo "LEADER_READY"; break; }
  sleep 2
done
pane | grep -v "^$" | tail -8
