"""
minimal SWE agent —— function calling 版（改进版）

相对上一版的两个改进：
改进1：try/except 错误处理 —— 工具出错时喂回错误给模型，而不是崩溃
改进2：final_answer 工具 —— 让"任务完成"更明确，不再靠猜
"""
import os
import json
import subprocess
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # 自动从 .env 文件读取环境变量（API key 不用每次 export 了）

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

SYSTEM_PROMPT = """你是一个编程 agent，负责完成用户交给你的编程任务。
请使用提供的工具来读取文件、修改文件、运行命令，最终修复问题并用测试验证。
任务完成后，必须调用 final_answer 工具给出最终回答。"""

# 工具定义：三个工具 + 一个 final_answer 工具
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
    {
        "type": "function",
        "function": {
            "name": "final_answer",
            "description": "给出最终回答，任务完成时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string", "description": "最终回答的内容"}
                },
                "required": ["answer"],
            },
        },
    },
]


def call_llm(messages):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=TOOLS,
    )
    return resp.choices[0].message


# ---------- 工具函数 ----------
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
    elif name == "final_answer":
        return args["answer"]
    return f"未知工具：{name}"


# ---------- 核心循环 ----------
def agent(task):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    for step in range(15):
        message = call_llm(messages)

        if message.tool_calls:
            messages.append(message)

            for tool_call in message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"\n===== 第 {step+1} 步：调用工具 {name} =====")

                # 改进1：错误处理——出错不崩溃，把错误喂回给模型
                try:
                    result = execute_tool(name, args)
                except Exception as e:
                    result = f"工具执行出错：{e}"
                print(f"返回：{str(result)[:150]}")

                # 改进2：如果调用的是 final_answer，直接返回
                if name == "final_answer":
                    print(f"\n✅ 任务完成，最终回答：\n{result}")
                    return result

                # 把工具结果喂回（final_answer 不会走到这里）
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })
        else:
            # 兜底：模型直接输出文字（没有调工具），也当作完成
            print(f"\n✅ 任务完成，最终回答：\n{message.content}")
            return message.content

    return "达到最大步数，未完成"


if __name__ == "__main__":
    task = input("请输入任务：")
    agent(task)
