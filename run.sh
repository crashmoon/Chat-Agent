#!/bin/bash

# 定义会话名称变量
SESSION_NAME="chat-app"

# 定义文件路径变量
SCRIPT_PATH="/home/csmn/Chat-Agent/app_on_xybot.py"

# 杀掉之前名为 $SESSION_NAME 的 tmux 会话
tmux kill-session -t $SESSION_NAME 2>/dev/null
sleep 1

# 创建一个新的名为 $SESSION_NAME 的 tmux 会话
tmux new-session -d -s $SESSION_NAME
sleep 1

# 在 tmux 会话中运行 bash
tmux send-keys -t $SESSION_NAME 'bash' C-m
sleep 1

# 在 tmux 会话中运行 conda 激活和 python 脚本
tmux send-keys -t $SESSION_NAME "source activate base && python $SCRIPT_PATH" C-m