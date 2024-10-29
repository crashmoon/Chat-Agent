#!/bin/bash

# 查找僵尸进程
zombie_pids=$(ps aux | awk '$8=="Z" {print $2}')

if [ -z "$zombie_pids" ]; then
  echo "没有僵尸进程。"
  exit 0
fi

echo "找到以下僵尸进程：$zombie_pids"

for pid in $zombie_pids; do
  # 找到僵尸进程的父进程 ID
  ppid=$(ps -o ppid= -p $pid)
  echo "僵尸进程 $pid 的父进程 ID 是 $ppid"

  # 终止父进程
  sudo kill -9 $ppid
  echo "已终止父进程 $ppid"
done

echo "僵尸进程已清理。"