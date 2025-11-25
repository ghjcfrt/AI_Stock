import os
from openai import OpenAI
import yfinance as yf  # 导入用于获取金融数据的库
import pandas as pd
from datetime import datetime

client=OpenAI(
# 从环境变量中获取 OpenAI API 密钥
api_key = os.getenv("OPENAI_API_KEY"),
# 设置 OpenAI API 的 URL
base_url = "https://api.gpt.ge/v1"  # 使用新版API的自定义基础URL
)
# 金融分析助手的系统提示
messages = [
    {"role": "system", "content": "你是一个专业的AI金融分析助手，擅长股票预测、企业财务分析和宏观经济分析。你可以根据数据进行详细的财务建模和量化分析。"}
]

if not client.api_key:
    raise ValueError("API 密钥未设置，请在环境变量中配置 'OPENAI_API_KEY'。")

# 获取股票历史数据
def get_stock_data(ticker, period='1y'):
    stock = yf.Ticker(ticker)
    return stock.history(period=period)

# 分析股票数据并生成总结
def analyze_stock_data(ticker):
    data = get_stock_data(ticker)
    if data.empty:
        return f"未能找到股票代码 {ticker} 的数据。"
    
    # 简单的分析，例如计算股票的平均价格、波动性等
    average_price = data['Close'].mean()
    volatility = data['Close'].std()
    recent_price = data['Close'][-1]
    
    analysis_summary = (
        f"股票代码: {ticker}\n"
        f"近期价格: {recent_price:.2f}\n"
        f"过去一年的平均价格: {average_price:.2f}\n"
        f"波动性（标准差）: {volatility:.2f}\n"
    )
    
    return analysis_summary

# 主循环
while True:
    user_input = input("请输入金融问题或股票代码（输入“退出”结束对话）: ")

    if user_input.lower() in ["退出", "exit"]:
        print("对话结束。")
        break

    if user_input.startswith("股票:"):  # 处理股票数据请求
        ticker = user_input.split(":")[1].strip().upper()  # 提取股票代码
        stock_summary = analyze_stock_data(ticker)  # 分析股票数据并生成总结
        print("分析结果:\n", stock_summary)  # 打印分析结果
        continue
    
    # 将用户问题加入对话
    messages.append({"role": "user", "content": user_input})

    # 调用 OpenAI API 获取AI回复
    try:
        completion = client.chat.completions.create(  # 使用新版API的调用方式
            model="gpt-4o",  # 使用更高级的GPT模型
            messages=messages,
        )
        
        #下一行问题未修复
        bot_response = completion.choices[0].message.content  # 新版中使用 'text' 提取回复
        #print(completion.choices[0].message.content)
        print("AI助手:", bot_response)

        # 将AI的回复加入对话
        messages.append({"role": "assistant", "content": bot_response})

    except Exception as e:
        print(f"发生错误: {e}")
