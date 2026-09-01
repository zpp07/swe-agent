# Minimal SWE Agent

一个最小可用的软件工程 AI Agent，能够自主地**读取代码、修改代码、运行测试**来修复 bug。

## 它能做什么

给定一个编程任务（例如"修复 buggy.py 里的 bug"），这个 agent 会：

1. 读取相关文件，理解代码
2. 定位问题，修改代码
3. 运行测试验证修复
4. 报告最终结果

整个过程是一个 **ReAct 循环**：思考 → 行动（调用工具）→ 观察结果 → 再思考，直到任务完成。

## 技术要点

- **ReAct 循环**：Agent 通过"行动—观察"的循环自主完成多步任务
- **Function Calling**：使用 DeepSeek API 的结构化工具调用，让模型稳定地、精确地调用工具（而非解析自由文本）
- **三个工具**：`read_file`（读文件）、`write_file`（写文件）、`run_command`（运行 shell 命令）

## 项目结构

```
swe-agent/
├── agent.py       # 核心：ReAct 循环 + function calling + 工具定义
├── buggy.py       # 测试用：一个带 bug 的示例文件
├── test_api.py    # API 连通性测试
└── README.md
```

## 运行方式

1. 安装依赖：

   ```bash
   pip install openai
   ```

2. 设置 API key（环境变量）：

   ```bash
   export DEEPSEEK_API_KEY="sk-你的key"
   ```

3. 运行：

   ```bash
   python agent.py
   ```

   然后输入任务，例如：`修复 buggy.py 里的 bug`

## 依赖

- Python 3.x
- [openai](https://github.com/openai/openai-python) 库
- DeepSeek API key（[https://platform.deepseek.com](https://platform.deepseek.com)）

## 后续改进方向

- [ ] 支持多文件操作与代码搜索
- [ ] 增加 `search` 工具，定位相关代码
- [ ] 使用 `deepseek-reasoner`（R1）增强推理能力
- [ ] 增加 token 用量统计与成本控制
