#!/bin/bash
# 一键运行 agent：进入目录 + 激活 venv + 运行
cd ~/swe-agent
source .venv/Scripts/activate
python agent.py
