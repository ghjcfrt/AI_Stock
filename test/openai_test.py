'''
import os
import openai

openai.api_key = "sk-4q3nsX8FfSd8vxdlE1806045E6234587Bd32EfA131B2F8C5"

openai.base_url = "https://api.gpt.ge/v1/"
openai.default_headers = {"x-foo": "true"}

completion = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": "你好",
        },
    ],
)
print(completion.choices[0].message.content)
'''


import os  # 导入操作系统模块
import openai  # 导入 OpenAI API 模块

# 设置 OpenAI API 的密钥
openai.api_key = "sk-4q3nsX8FfSd8vxdlE1806045E6234587Bd32EfA131B2F8C5"
# 设置 OpenAI API 的基础 URL
openai.base_url = "https://api.gpt.ge/v1/"
# 设置默认请求头
openai.default_headers = {"x-foo": "true"}

# 记录对话的历史
messages = []

while True:  # 开始一个无限循环，持续进行对话
    user_input = input("你: ")  # 获取用户输入
    if user_input.lower() in ["退出", "exit"]:  # 如果用户输入“退出”或“exit”，则结束对话
        print("对话结束。")
        break  # 退出循环
    
    messages.append({"role": "user", "content": user_input})  # 将用户的输入添加到消息历史中

    # 调用 OpenAI API 来获取机器人的回复
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # 指定使用的模型
        messages=messages,  # 传递消息历史
    )
    
    bot_response = completion.choices[0].message.content  # 提取机器人的回复
    print("机器人:", bot_response)  # 打印机器人的回复

    # 将机器人的回复也加入到消息历史中
    messages.append({"role": "assistant", "content": bot_response})
