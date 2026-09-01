"""
minimal SWE agent —— function calling 版

用 API 的 function calling（结构化工具调用）代替"解析文字"。
模型不再输出自由文字，而是输出结构化的工具调用 JSON。
"""
import os
import json
import subprocess
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

# 系统提示词（不再需要教模型"输出格式"，因为工具是用 tools 参数声明的）
SYSTEM_PROMPT = """你是一个编程 agent，负责完成用户交给你的编程任务。
请使用提供的工具来读取文件、修改文件、运行命令，最终修复问题并用测试验证。"""

# 工具定义：用 JSON schema 声明，API 会强制模型输出结构化的调用
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取指定文件的完整内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "覆盖写入指定文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "要写入的完整内容"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "运行 shell 命令并返回输出",
            "parameters": {
                "type": "object",
                "properties": {
                    "cmd": {"type": "string", "description": "要执行的命令"}
                },
                "required": ["cmd"],
            },
        },
    },
]


def call_llm(messages):
    """调用大模型（带 tools 参数），返回完整的 message 对象"""
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=TOOLS,
    )
    return resp.choices[0].message


# ---------- 三个工具（和之前一样） ----------
def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"已写入 {path}"


def run_command(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (r.stdout + r.stderr) or "(无输出)"


def execute_tool(name, args):
    """根据工具名分发执行"""
    if name == "read_file":
        return read_file(args["path"])
    elif name == "write_file":
        return write_file(args["path"], args["content"])
    elif name == "run_command":
        return run_command(args["cmd"])
    return f"未知工具：{name}"


# ---------- 核心循环 ----------
def agent(task):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    for step in range(15):
        message = call_llm(messages)

        # 关键区别：不再解析文字，而是检查 message.tool_calls
        if message.tool_calls:
            # 把模型的 tool_call 消息加入历史（这是下一步 API 需要的）
            messages.append(message)

            for tool_call in message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)  # 结构化参数
                print(f"\n===== 第 {step+1} 步：调用工具 {name} =====")
                print(f"参数：{args}")
                result = execute_tool(name, args)
                print(f"返回：{result[:150]}")

                # 用专门的 "tool" 角色把结果喂回
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            # 没有 tool_calls，说明模型认为任务完成，输出最终回答
            print(f"\n✅ 任务完成，最终回答：\n{message.content}")
            return message.content

    return "达到最大步数，未完成"


if __name__ == "__main__":
    task = input("请输入任务：")
    agent(task)
