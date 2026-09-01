"""
测试 DeepSeek API 是否能连通。

运行前先在终端设置环境变量（把你的 key 填进去）：
    export DEEPSEEK_API_KEY="sk-你的key"
然后运行：
    python test_api.py
"""
import os
from openai import OpenAI

# 从环境变量读取 API key（安全做法，不硬编码在代码里）
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",   # 指向 DeepSeek，而不是默认的 OpenAI
)

# 发一条最简单的消息，测试能不能连通
response = client.chat.completions.create(
    model="deepseek-chat",   # 便宜快速的 V3；也可换 deepseek-reasoner（R1，更强但慢）
    messages=[
        {"role": "user", "content": "用一句话解释什么是注意力机制"},
    ],
)

# 打印模型的回答
print(response.choices[0].message.content)
