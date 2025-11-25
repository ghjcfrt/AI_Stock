# '''
#                        _oo0oo_
#                       o8888888o
#                       88" . "88
#                       (| -_- |)
#                       0\  =  /0
#                     ___/`---'\___
#                   .' \\|     |// '.
#                  / \\|||  :  |||// \
#                 / _||||| -:- |||||- \
#                |   | \\\  - /// |   |
#                | \_|  ''\---/''  |_/ |
#                \  .-\__  '-'  ___/-. /
#              ___'. .'  /--.--\  `. .'___
#           ."" '<  `.___\_<|>_/___.' >' "".
#          | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#          \  \ `_.   \_ __\ /__ _/   .-` /  /
#      =====`-.____`.___ \_____/___.-`___.-'=====
#                        `=---='
#
#
#      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#            佛祖保佑     永不宕机     永无BUG
# '''

import os  # 汇入 os 套件
import textwrap  # 汇入 textwrap 套件
from datetime import datetime, time  # 汇入 datetime 套件

import google.generativeai as genai  # 汇入 google.generativeai 套件
import numpy as np  # 汇入 numpy 套件
import requests  # 汇入 requests 套件
import talib as ta  # 汇入 talib 套件
import yfinance as yf  # 汇入 yfinance 套件
from bs4 import BeautifulSoup  # 汇入 BeautifulSoup 套件

from openai import OpenAI  # 汇入 OpenAI 套件

# import pandas as pd # 汇入 pandas 套件

# 显示当前日期和时间
now = datetime.now()  # 取得当前时间
print(f"当前日期和时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")  # 印出日期和时间

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 设定参数
api_key = ""  # 请替换为您的 Gemini API Key，留空则不启用

client = OpenAI(
    # 从环境变量中获取 OpenAI API 密钥
    api_key=os.getenv("OPENAI_API_KEY"),
    # 设置 OpenAI API 的 URL
    base_url="https://api.gpt.ge/v1",  # 使用新版API的自定义基础URL
)

ticker = input("请输入股票代码（请注意输入国际股票代码）: ")  # 要分析的股票代码
buy_price = input(
    "请输入购买价格（建议保留小数点后两位）: "
)  # 您的购买价格，留空则忽略
buy_price = float(buy_price)  # 您的购买价格，留空则忽略
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 使用 Yahoo Finance 抓取即时股价
# def fetch_real_time_price(ticker):  # 定义 fetch_real_time_price 函数
#     url = f'https://tw.stock.yahoo.com/quote/{ticker}'  # 设定 Yahoo Finance 网址      ******会有无法抓取问题******
#     response = requests.get(url)  # 取得网页回应

#     if response.status_code == 200:  # 网页回应成功
#         soup = BeautifulSoup(response.text, "html.parser")  # 解析网页
#         price_element = soup.select_one(r'.Fz\(32px\)')  # 选取股价元素
#         # price_element = soup.find("span", class_="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)").text
#         if price_element:  # 股价元素存在
#             try:  # 尝试转换股价为浮点数
#                 current_price = float(
#                     price_element.get_text().replace(',', ''))  # 转换股价为浮点数
#                 return current_price  # 回传股价
#             except ValueError:  # 转换失败
#                 return None  # 回传 None
#         else:
#             return None  # 股价元素不存在
#     else:
#         return None  # 网页回应失败


# 优化后的抓取函数
def fetch_real_time_price(ticker):
    url = f"https://tw.stock.yahoo.com/quote/{ticker}"  # 设置 Yahoo Finance URL      ******tun模式******
    # url = f'https://hk.finance.yahoo.com/quote/{ticker}'  # 设定 Yahoo Finance 网址      ******会有403问题******
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept-Language": "en-US,en;q=0.9",  # 模拟浏览器的语言首选项为英文
        "Referer": "https://tw.stock.yahoo.com",  # 设置来源页面为Yahoo财经主页
        "Connection": "keep-alive",  # 保持连接活跃
    }  # 模拟浏览器的User-Agent

    try:
        response = requests.get(
            url, headers=headers
        )  # 获取网页响应，并加入headers避免被反爬机制阻挡

        if response.status_code == 200:  # 确认响应成功
            soup = BeautifulSoup(response.text, "html.parser")  # 解析HTML内容
            # 将soup的内容写入html文件
            with open(
                r"D:\code\Python\aistock\error\webpage_content.html",
                "w",
                encoding="utf-8",
            ) as file:
                file.write(soup.prettify())

            price_element = soup.select_one(r".Fz\(32px\)")  # 选择股价元素
            # price_element = soup.select_one(r'.Fz\(32px\).Fw\(b\).Lh\(1\).Mend\(4px\).D\(f\).Ai\(c\).C\(\$c-trend-down\)')  # 更全的索引信息

            if price_element:  # 如果找到股价元素
                try:
                    # 尝试将抓取到的文字转换为浮点数
                    current_price = float(price_element.get_text().replace(",", ""))
                    return current_price  # 成功抓取并转换后返回股价
                except ValueError:  # 如果转换出错
                    print("错误: 无法将价格转换为浮点数。")
                    return None
            else:
                print("错误: 未找到价格元素。")
                return None
        else:
            print(f"错误: 获取网页失败，状态码: {response.status_code}")
            return None

    except Exception as e:
        print(f"发生错误: {e}")
        return None


# 在分析股票之前先抓取最新价格
current_price = fetch_real_time_price(ticker)  # 取得股价
if current_price:  # 股价抓取成功
    print(f"{ticker} 的当前股价为: {current_price} TWD")  # 印出股价
else:
    print("未能成功抓取股价")  # 股价抓取失败
    exit()  # 结束程式


# 检查当前时间是否在市场交易时间内
def is_market_open():
    now = datetime.now()
    market_open_time = time(9, 0)  # 假设市场开盘时间为上午9点
    market_close_time = time(13, 30)  # 假设市场收盘时间为下午1点30分
    return (
        market_open_time <= now.time() <= market_close_time
    )  # 检查是否在市场交易时间内


# 计算 MACD 指标
def calculate_macd(
    prices, fastperiod=12, slowperiod=26, signalperiod=9
):  # 定义 calculate_macd 函数
    macd, macd_signal, macd_diff = ta.MACD(
        prices, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod
    )  # 计算 MACD 指标
    return macd, macd_signal, macd_diff  # 回传 MACD 值、SIGNAL 值、DIFF 值


# 计算 RSI 指标
def calculate_rsi(prices, timeperiod=14):
    return ta.RSI(prices, timeperiod)


# 计算布林带（Bollinger Bands）
def calculate_bollinger_bands(prices, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0):
    """
    计算布林带
    :param prices: 股票价格数据（例如收盘价）
    :param timeperiod: 计算移动平均线的週期，默认为20
    :param nbdevup: 上轨带距离移动平均线的标准差倍数，默认为2
    :param nbdevdn: 下轨带距离移动平均线的标准差倍数，默认为2
    :param matype: 移动平均类型，默认为0（简单移动平均）
    :return: upperband, middleband, lowerband
    """
    upperband, middleband, lowerband = ta.BBANDS(
        prices, timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=matype
    )
    return upperband, middleband, lowerband


# 计算随机震盪指标（Stochastic Oscillator）
def calculate_stochastic_oscillator(
    high, low, close, fastk_period=14, slowk_period=3, slowd_period=3
):
    """
    计算随机震盪指标
    :param high: 股票最高价数据
    :param low: 股票最低价数据
    :param close: 股票收盘价数据
    :param fastk_period: 快速K线的週期，默认为14
    :param slowk_period: 慢速K线的週期，默认为3
    :param slowd_period: 慢速D线的週期，默认为3
    :return: slowk, slowd
    """
    slowk, slowd = ta.STOCH(
        high,
        low,
        close,
        fastk_period=fastk_period,
        slowk_period=slowk_period,
        slowd_period=slowd_period,
    )
    return slowk, slowd


# 计算平均真实波幅（ATR）
def calculate_atr(high, low, close, timeperiod=14):
    """
    计算平均真实波幅（ATR）
    :param high: 股票最高价数据
    :param low: 股票最低价数据
    :param close: 股票收盘价数据
    :param timeperiod: 计算ATR的週期，默认为14
    :return: atr
    """
    atr = ta.ATR(high, low, close, timeperiod=timeperiod)
    return atr


# ***新增的趋势指标计算函数***


# 计算 EMA（Exponential Moving Average，指数移动平均线）
def calculate_ema(prices, timeperiod=20):
    return ta.EMA(prices, timeperiod=timeperiod)


# 计算 SMA（Simple Moving Average，简单移动平均线）
def calculate_sma(prices, timeperiod=50):
    return ta.SMA(prices, timeperiod=timeperiod)


# 计算 ADX（Average Directional Index，平均趋向指数）
def calculate_adx(high, low, close, timeperiod=14):
    return ta.ADX(high, low, close, timeperiod=timeperiod)


# **修正后的OBV计算函数**
def calculate_obv(close_prices, volumes):
    obv = np.zeros_like(close_prices)
    for i in range(1, len(close_prices)):
        if close_prices.iloc[i] > close_prices.iloc[i - 1]:  # 修改为使用 .iloc
            obv[i] = obv[i - 1] + volumes.iloc[i]  # 修改为使用 .iloc
        elif close_prices.iloc[i] < close_prices.iloc[i - 1]:  # 修改为使用 .iloc
            obv[i] = obv[i - 1] - volumes.iloc[i]  # 修改为使用 .iloc
        else:
            obv[i] = obv[i - 1]
    return obv


# **新增部分：计算 VWAP 指标**
def calculate_vwap(high, low, close, volume):
    typical_price = (high + low + close) / 3
    vwap = (typical_price * volume).cumsum() / volume.cumsum()
    return vwap


# 分析股票
def analyze_stock(ticker, buy_price):
    if not is_market_open():
        print("提醒：当前时间不在市场交易时间内，数据可能不完整或不准确。")

    stock = yf.Ticker(ticker)

    try:
        info = stock.info
        quote_type = info.get("quoteType", "UNKNOWN")
    except Exception as e:
        print(f"从 Yahoo Finance 获取数据时出现错误: {e}")
        info = {}
        quote_type = "UNKNOWN"

    # 获取股票或 ETF 的信息
    try:
        info = stock.info
        quote_type = info.get("quoteType", "UNKNOWN")
    except Exception as e:
        print(f"从 Yahoo Finance 获取数据时出现错误: {e}")
        info = {}
        quote_type = "UNKNOWN"

    if quote_type == "ETF":  # 判断是否为 ETF
        return analyze_etf(stock, buy_price, info)  # 分析 ETF
    else:
        return analyze_equity(stock, buy_price)  # 分析股票


# 分析 ETF 的函数
def analyze_etf(stock, buy_price, info):
    # 使用 `info` 中的 ETF 特有资料
    aum = info.get("totalAssets", "无法取得")
    expense_ratio = info.get("expenseRatio", "无法取得")
    ytd_return = info.get("ytdReturn", "无法取得")
    three_year_return = info.get("threeYearAverageReturn", "无法取得")
    five_year_return = info.get("fiveYearAverageReturn", "无法取得")
    fifty_two_week_low = info.get("fiftyTwoWeekLow", "无法取得")
    fifty_two_week_high = info.get("fiftyTwoWeekHigh", "无法取得")
    fifty_day_avg = info.get("fiftyDayAverage", "无法取得")
    two_hundred_day_avg = info.get("twoHundredDayAverage", "无法取得")
    volume = info.get("volume", "无法取得")
    average_volume = info.get("averageVolume", "无法取得")
    beta = info.get("beta3Year", "无法取得")

    # 取得 ETF 的历史价格数据和技术指标
    stock_data = stock.history(
        start="2021-01-01", end=datetime.now().strftime("%Y-%m-%d")
    )

    # 使用 'Adj Close' 列，如果不存在则使用 'Close'
    if "Adj Close" not in stock_data.columns:
        stock_data["Adj Close"] = stock_data["Close"]

    # 计算动量指标
    stock_data["upperband"], stock_data["middleband"], stock_data["lowerband"] = (
        calculate_bollinger_bands(stock_data["Adj Close"])
    )
    stock_data["slowk"], stock_data["slowd"] = calculate_stochastic_oscillator(
        stock_data["High"], stock_data["Low"], stock_data["Close"]
    )
    stock_data["atr"] = calculate_atr(
        stock_data["High"], stock_data["Low"], stock_data["Close"]
    )

    # 计算 MACD 和 RSI
    stock_data["macd"], stock_data["macd_signal"], stock_data["macd_diff"] = (
        calculate_macd(stock_data["Adj Close"])
    )
    stock_data["rsi"] = calculate_rsi(stock_data["Adj Close"])

    # ***新增的趋势指标计算***
    stock_data["ema_20"] = calculate_ema(stock_data["Adj Close"])
    stock_data["sma_50"] = calculate_sma(stock_data["Adj Close"])
    stock_data["adx"] = calculate_adx(
        stock_data["High"], stock_data["Low"], stock_data["Close"]
    )

    # 取得股息纪录
    dividends = stock.dividends

    # 返回分析结果
    return {
        "aum": aum,
        "expense_ratio": expense_ratio,
        "ytd_return": ytd_return,
        "three_year_return": three_year_return,
        "five_year_return": five_year_return,
        "fifty_two_week_low": fifty_two_week_low,
        "fifty_two_week_high": fifty_two_week_high,
        "fifty_day_avg": fifty_day_avg,
        "two_hundred_day_avg": two_hundred_day_avg,
        "volume": volume,
        "average_volume": average_volume,
        "beta": beta,
        "dividends": dividends,
        "current_price": stock_data["Adj Close"].iloc[-1],
        "rsi": stock_data["rsi"].iloc[-1],
        "macd": stock_data["macd"].iloc[-1],
        "macd_signal": stock_data["macd_signal"].iloc[-1],
        "ema_20": stock_data["ema_20"].iloc[-1],  # ***新增的EMA指标结果***
        "sma_50": stock_data["sma_50"].iloc[-1],  # ***新增的SMA指标结果***
        "adx": stock_data["adx"].iloc[-1],  # ***新增的ADX指标结果***
    }


# 格式化 ETF 分析文本
def format_etf_analysis_text(result):
    def format_value(value, fmt="{:.2f}", default="无法取得"):
        if isinstance(value, (int, float)):
            return fmt.format(value)
        elif isinstance(value, str):
            return value
        else:
            return default

    analysis_text = f"""
    ETF 分析报告 ({ticker}):

    **基金基本资料:**
    - 基金规模 (AUM): {format_value(result['aum'], "{:,.0f}")} TWD
    - 费用率: {format_value(result['expense_ratio'], "{:.2f}")}%
    - 年初至今回报率 (YTD Return): {format_value(result['ytd_return'], "{:.2%}")}%
    - 三年平均回报率: {format_value(result['three_year_return'], "{:.2%}")}%
    - 五年平均回报率: {format_value(result['five_year_return'], "{:.2%}")}%

    **价格区间:**
    - 52周最低价: {format_value(result['fifty_two_week_low'])} TWD
    - 52周最高价: {format_value(result['fifty_two_week_high'])} TWD
    - 50天平均价: {format_value(result['fifty_day_avg'])} TWD
    - 200天平均价: {format_value(result['two_hundred_day_avg'])} TWD

    **技术指标:**
    - 当前价格: {format_value(result['current_price'])} TWD
    - 相对强弱指数 (RSI): {format_value(result['rsi'])}
    - MACD: {format_value(result['macd'])}
    - MACD Signal: {format_value(result['macd_signal'])}
    - EMA 20日: {format_value(result['ema_20'])} TWD  # ***新增的EMA结果***
    - SMA 50日: {format_value(result['sma_50'])} TWD  # ***新增的SMA结果***
    - ADX: {format_value(result['adx'])}             # ***新增的ADX结果***
    - 成交量: {format_value(result['volume'])}
    - 平均成交量: {format_value(result['average_volume'])}
    - 三年贝塔系数: {format_value(result['beta'])}

    **股息记录:**
    - {result['dividends'].tail() if result['dividends']
    is not None else '无法取得'}
    """
    return textwrap.dedent(analysis_text).strip()


# 分析股票的函数
def analyze_equity(stock, buy_price):
    # 先抓取最新的股价
    current_price = fetch_real_time_price(ticker)

    # 取得历史价格数据
    stock_data = stock.history(
        start="2021-01-01", end=datetime.now().strftime("%Y-%m-%d")
    )

    # 检查是否有 'Adj Close' 列，如果没有则使用 'Close'
    closing_column = "Adj Close" if "Adj Close" in stock_data.columns else "Close"

    # 如果成功获取到实时价格，使用实时价格替代历史数据中的最后一个收盘价
    if current_price:
        stock_data.loc[stock_data.index[-1], closing_column] = current_price
    else:
        current_price = stock_data[closing_column].iloc[-1]

    # 获取股票的相关信息
    try:
        info = stock.info
        quote_type = info.get("quoteType", "UNKNOWN")
    except Exception as e:
        print(f"从 Yahoo Finance 获取数据时出现错误: {e}")
        info = {}
        quote_type = "UNKNOWN"

    # 取得股息和拆股信息
    dividends = stock.dividends
    splits = stock.splits

    # 取得财务报表
    balance_sheet = stock.balance_sheet
    income_statement = stock.financials
    cashflow = stock.cashflow

    # 提取资产负债表的主要项目
    total_assets = (
        balance_sheet.loc["Total Assets"].iloc[0]
        if "Total Assets" in balance_sheet.index
        else "无法取得"
    )
    total_liabilities = (
        balance_sheet.loc["Total Liab"].iloc[0]
        if "Total Liab" in balance_sheet.index
        else "无法取得"
    )
    total_equity = (
        balance_sheet.loc["Total Stockholder Equity"].iloc[0]
        if "Total Stockholder Equity" in balance_sheet.index
        else "无法取得"
    )

    # 新增财务槓杆指标
    debt_to_equity = info.get("debtToEquity", "无法取得")
    interest_coverage = info.get("interestCoverage", "无法取得")

    # 取得估值指标
    price_to_book = info.get("priceToBook", "无法取得")
    price_to_sales = info.get("priceToSalesTrailing12Months", "无法取得")
    dividend_yield = info.get("dividendYield", "无法取得")

    # 获取市场资本化、市盈率等数据
    market_cap = info.get("marketCap", "无法取得")
    pe_ratio = info.get("trailingPE", "无法取得")
    eps = info.get("trailingEps", "无法取得")
    industry = info.get("industry", "无法取得")
    description = info.get("longBusinessSummary", "无法取得")

    # 新增经营现金流和自由现金流部分
    operating_cash_flow = info.get("operatingCashflow", "无法取得")
    free_cashflow = info.get("freeCashflow", "无法取得")

    # 新增盈利能力指标计算部分
    revenue = info.get("totalRevenue")
    cost_of_goods_sold = info.get("costOfRevenue")
    operating_income = info.get("operatingIncome")
    net_income = info.get("netIncome")

    profitability_indicators = {}
    profitability_indicators["gross_margin"] = (
        (revenue - cost_of_goods_sold) / revenue
        if revenue and cost_of_goods_sold
        else "无法计算"
    )
    profitability_indicators["operating_margin"] = (
        operating_income / revenue if revenue and operating_income else "无法计算"
    )
    profitability_indicators["net_profit_margin"] = (
        net_income / revenue if revenue and net_income else "无法计算"
    )

    # 处理财务比率
    current_ratio = info.get("currentRatio", "无法取得")
    quick_ratio = info.get("quickRatio", "无法取得")
    profit_margin = info.get("profitMargins", "无法取得")

    # 获取 ROA
    roa = info.get("returnOnAssets", "无法取得")

    # 处理财务数据异常
    try:
        recommendations = stock.recommendations
    except Exception as e:
        recommendations = "无法取得推荐数据"
        print(f"从 Yahoo Finance 获取推荐数据时出现错误: {e}")

    # 取得自由现金流
    free_cashflow = info.get("freeCashflow")

    # 取得收益增长率
    earnings_growth = info.get("earningsGrowth")

    # 取得收入增长率
    revenue_growth = info.get("revenueGrowth")

    # 取得净利润率
    net_profit_margin = info.get("netProfitMargins")

    # 取得股东权益回报率 (ROE)
    roe = info.get("returnOnEquity")

    # 取得企业价值
    enterprise_value = info.get("enterpriseValue")

    # 取得每股净资产 (BVPS)
    bvps = info.get("bookValue")

    # 取得分析师推荐
    try:
        recommendations = stock.recommendations
    except Exception as e:
        recommendations = "无法取得推荐数据"
        print(f"从 Yahoo Finance 获取推荐数据时出现错误: {e}")

    # 取得贝塔系数
    beta = info.get("beta")

    # 取得股东信息
    try:
        major_holders = stock.major_holders
        institutional_holders = stock.institutional_holders
    except Exception as e:
        major_holders = "无法获取主要股东信息"
        institutional_holders = "无法获取机构持股信息"
        print(f"从 Yahoo Finance 获取股东信息时出现错误: {e}")

    # 从财务报表中取得净利润和收入，并手动计算收入增长率和净利润率
    try:
        total_revenue_current = income_statement.loc["Total Revenue"].iloc[0]
        total_revenue_previous = income_statement.loc["Total Revenue"].iloc[1]
        revenue_growth = (
            (total_revenue_current - total_revenue_previous)
            / total_revenue_previous
            * 100
        )

        net_income_current = income_statement.loc["Net Income"].iloc[0]
        net_income_previous = income_statement.loc["Net Income"].iloc[1]
        earnings_growth = (
            (net_income_current - net_income_previous) / net_income_previous * 100
        )
        net_profit_margin = (net_income_current / total_revenue_current) * 100
    except KeyError:
        print("无法取得净利润或收入数据，无法计算净利润率或增长率。")
        revenue_growth = None
        earnings_growth = None
        net_profit_margin = None

    # 计算技术指标
    stock_data["macd"], stock_data["macd_signal"], stock_data["macd_diff"] = (
        calculate_macd(stock_data[closing_column])
    )
    delta = stock_data[closing_column].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    stock_data["rsi"] = rsi

    # 新增动量指标
    stock_data["upperband"], stock_data["middleband"], stock_data["lowerband"] = (
        calculate_bollinger_bands(stock_data[closing_column])
    )
    stock_data["slowk"], stock_data["slowd"] = calculate_stochastic_oscillator(
        stock_data["High"], stock_data["Low"], stock_data["Close"]
    )
    stock_data["atr"] = calculate_atr(
        stock_data["High"], stock_data["Low"], stock_data["Close"]
    )

    # ***新增的趋势指标计算***
    stock_data["ema_20"] = calculate_ema(stock_data[closing_column])
    stock_data["sma_50"] = calculate_sma(stock_data[closing_column])
    stock_data["adx"] = calculate_adx(
        stock_data["High"], stock_data["Low"], stock_data["Close"]
    )

    # **新增部分：计算 OBV 和 VWAP**
    stock_data["obv"] = calculate_obv(stock_data["Close"], stock_data["Volume"])
    stock_data["vwap"] = calculate_vwap(
        stock_data["High"], stock_data["Low"], stock_data["Close"], stock_data["Volume"]
    )

    # 如果 buy_price 为 None，跳过年化回报率的计算
    if buy_price:
        annual_return = (stock_data[closing_column].iloc[-1] / buy_price) ** (1 / 3) - 1
    else:
        annual_return = None

    result = {
        "current_price": current_price,
        "rsi": stock_data["rsi"].iloc[-1],
        "macd": stock_data["macd"].iloc[-1],
        "macd_signal": stock_data["macd_signal"].iloc[-1],
        "annual_return": annual_return * 100
        if annual_return is not None
        else "无法计算",
        "price_to_book": price_to_book,
        "price_to_sales": price_to_sales,
        "dividend_yield": dividend_yield * 100
        if dividend_yield != "无法取得"
        else "无法取得",
        "buy_price": buy_price,
        "dividends": dividends,
        "splits": splits,
        "balance_sheet": balance_sheet,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
        "income_statement": income_statement,
        "cashflow": cashflow,
        "market_cap": market_cap,
        "pe_ratio": pe_ratio,
        "eps": eps,
        "industry": industry,
        "description": description,
        "recommendations": recommendations,
        "beta": beta,
        "current_ratio": current_ratio,
        "quick_ratio": quick_ratio,
        "profit_margin": profit_margin,
        "free_cashflow": free_cashflow,
        "operating_cash_flow": operating_cash_flow,
        "earnings_growth": earnings_growth,
        "revenue_growth": revenue_growth,
        "net_profit_margin": net_profit_margin,
        "roe": roe,
        "enterprise_value": enterprise_value,
        "bvps": bvps,
        "major_holders": major_holders,
        "institutional_holders": institutional_holders,
        "upperband": stock_data["upperband"].iloc[-1],
        "middleband": stock_data["middleband"].iloc[-1],
        "lowerband": stock_data["lowerband"].iloc[-1],
        "slowk": stock_data["slowk"].iloc[-1],
        "slowd": stock_data["slowd"].iloc[-1],
        "atr": stock_data["atr"].iloc[-1],
        "ema_20": stock_data["ema_20"].iloc[-1],
        "sma_50": stock_data["sma_50"].iloc[-1],
        "adx": stock_data["adx"].iloc[-1],
        "obv": stock_data["obv"].iloc[-1],
        "vwap": stock_data["vwap"].iloc[-1],
        "gross_margin": profitability_indicators["gross_margin"],
        "operating_margin": profitability_indicators["operating_margin"],
        "net_profit_margin": profitability_indicators["net_profit_margin"],
        "debt_to_equity": debt_to_equity,
        "interest_coverage": interest_coverage,
        "roa": roa,
    }

    return result


# 格式化股票分析文本
def format_analysis_text(result):
    def format_value(value, fmt="{:.2f}", default="无法取得"):
        if isinstance(value, (int, float)):
            return fmt.format(value)
        elif isinstance(value, str):
            return value
        else:
            return default

    def format_dataframe(df, default="无法取得"):
        if df is None or df.empty:
            return default
        else:
            return df.tail(5).to_string()  # 只显示最近5行，防止显示过长

    analysis_text = f"""
    股票分析报告 ({ticker}):

    **股价和技术分析:**
    - 当前价格: {format_value(result['current_price'])} TWD
    - 购买价格: {format_value(result['buy_price']) if result['buy_price'] is not None else '无法取得'} TWD
    - 年化回报率: {format_value(result['annual_return'])}%
    - 相对强弱指数 (RSI): {format_value(result['rsi'])}
    - MACD: {format_value(result['macd'])}
    - MACD Signal: {format_value(result['macd_signal'])}

    **布林带指标:**
    - 上轨带: {format_value(result['upperband'])} TWD
    - 中轨带: {format_value(result['middleband'])} TWD
    - 下轨带: {format_value(result['lowerband'])} TWD

    **随机震盪指标:**
    - 慢速K线: {format_value(result['slowk'])}
    - 慢速D线: {format_value(result['slowd'])}

    **平均真实波幅 (ATR):**
    - ATR: {format_value(result['atr'])}

    **趋势指标:**
    - EMA 20日: {format_value(result['ema_20'])} TWD
    - SMA 50日: {format_value(result['sma_50'])} TWD
    - ADX: {format_value(result['adx'])}

    **成交量指标:**
    - OBV: {format_value(result['obv'])}
    - VWAP: {format_value(result['vwap'])} TWD

    **公司信息:**
    - 市场资本化: {format_value(result['market_cap'], "{:,.0f}")} TWD
    - 市盈率: {result.get('pe_ratio', '无法取得')}
    - 每股收益 (EPS): {result.get('eps', '无法取得')}
    - 行业: {result.get('industry', '无法取得')}
    - 公司描述: {result.get('description', '无法取得')}

    **估值指标:**
    - 市净率 (P/B): {format_value(result['price_to_book'])}
    - 市销率 (P/S): {format_value(result['price_to_sales'])}
    - 股息率 (Dividend Yield): {format_value(result['dividend_yield'])}%

    **财务比率:**
    - 当前比率: {result.get('current_ratio', '无法取得')}
    - 速动比率: {result.get('quick_ratio', '无法取得')}
    - 利润率: {result.get('profit_margin', '无法取得')}%

    **现金流指标:**
    - 经营现金流: {format_value(result['operating_cash_flow'])} TWD
    - 自由现金流: {format_value(result['free_cashflow'])} TWD

    **财务槓杆指标（Leverage Indicators）:**
    - 负债权益比率 (Debt to Equity Ratio): {format_value(result['debt_to_equity'])}
    - 利息保障倍数 (Interest Coverage Ratio): {format_value(result['interest_coverage'])}

    **增长率分析:**
    - 收益增长率: {result.get('earnings_growth', '无法取得')}%
    - 收入增长率: {result.get('revenue_growth', '无法取得')}%

    **盈利能力指标 (Profitability Indicators):**
    - 毛利率 (Gross Margin): {format_value(result['gross_margin'])}
    - 营业利润率 (Operating Margin): {format_value(result['operating_margin'])}
    - 净利润率 (Net Profit Margin): {format_value(result['net_profit_margin'])}

    **资产回报率 (ROA):**
    - {format_value(result['roa'], "{:.2%}")}

    **股东权益回报率 (ROE):**
    - {format_value(result['roe'], "{:.2%}")}

    **企业价值 (EV):**
    - {format_value(result['enterprise_value'], "{:,.0f}")} TWD

    **每股净资产 (BVPS):**
    - {result.get('bvps', '无法取得')}

    **资产负债表摘要:**
    - 总资产: {format_value(result['total_assets'], "{:,.0f}")} TWD
    - 总负债: {format_value(result['total_liabilities'], "{:,.0f}")} TWD
    - 股东权益总额: {format_value(result['total_equity'], "{:,.0f}")} TWD

    **财务报表摘要:**
    - 资产负债表: {result['balance_sheet'].head() if result['balance_sheet'] is not None else '无法取得'}
    - 损益表: {result['income_statement'].head() if result['income_statement'] is not None else '无法取得'}
    - 现金流量表: {result['cashflow'].head() if result['cashflow'] is not None else '无法取得'}

    **股息和拆股信息:**
    - 股息: {result['dividends'].tail() if result['dividends'] is not None else '无法取得'}
    - 拆股: {result['splits']}

    **分析师推荐:**
    - {result['recommendations'].tail() if result['recommendations']
       is not None else '无法取得'}

    **股东信息:**
    - 主要持股人: {result.get('major_holders', '无法取得')}
    - 机构持股人: {result.get('institutional_holders', '无法取得')}

    **贝塔系数 (Beta):**
    - {result.get('beta', '无法取得')}
    """
    return textwrap.dedent(analysis_text).strip()


# 使用Openai ChatGPT API生成报告
def generate_stock_analysis_with_chatgpt(client, analysis_text):
    if not client.api_key:
        raise ValueError("API 密钥未设置，请在环境变量中配置 'OPENAI_API_KEY'。")

    messages = [
        {
            "role": "system",
            "content": "你是一个专业的AI金融分析助手，擅长股票预测、企业财务分析和宏观经济分析。你可以根据数据进行详细的财务建模和量化分析。",
        },
        {
            "role": "user",
            "content": (
                "根据以下提供的资料，请为投资者制定当前最适合的投资策略，并逐项分析以下技术指标和财务指标的意义："
                "相对强弱指数（RSI）、MACD、布林带（Bollinger Bands）、"
                "成交量指标（如OBV和VWAP）、财务比率（如市盈率、股息率）、以及盈利能力指标（如毛利率、营业利润率）。"
                "特别要注意使用者的购入价格，根据当前价格提供止损建议。"
                "目前价格是应该卖出、持有还是继续买入，并针对不同的投资情境（如短期与长期）提出具体的下一步行动建议"
                "（如是否应调整仓位、关注其他市场趋势）。"
                "在分析中请考虑当前的市场环境和经济形势。"
                "总结部分请至少300字，并结合上述分析给出整体投资建议，使用简体中文回答：\n\n"
                f"{analysis_text}"
            ),
        },
    ]

    try:
        completion = client.chat.completions.create(  # 使用新版API的调用方式
            model="gpt-4o",  # 使用更高级的GPT模型
            messages=messages,
        )
        # 下一行问题未修复
        bot_response = completion.choices[
            0
        ].message.content  # 新版中使用 'text' 提取回复
        # print(completion.choices[0].message.content)
        # print("AI助手:", bot_response) # 是这里print的

        # 将AI的回覆加入对话
        messages.append({"role": "assistant", "content": bot_response})

    except Exception as e:
        print(f"发生错误: {e}")
    return bot_response  # 这是我刚加的


# 使用 Gemini API 生成报告
def generate_stock_analysis_with_gemini(api_key, analysis_text):
    if not api_key:
        return "Gemini API Key 未提供，将跳过 AI 生成的分析报告部分。"

    try:
        genai.configure(api_key=api_key)  # 设定Gemini API Key
        model = genai.GenerativeModel("gemini-1.5-flash")
        full_prompt = (
            f"你是一个专业股票分析师，根据以下提供的资料，请为投资者制定当前最适合的投资策略，并逐项分析以下技术指标和财务指标的意义："
            f"相对强弱指数（RSI）、MACD、布林带（Bollinger Bands）、成交量指标（如OBV和VWAP）、财务比率（如市盈率、股息率）、以及盈利能力指标（如毛利率、营业利润率）。"
            f"特别要注意使用者的购入价格，根据当前价格提供止损建议。目前价格是应该卖出、持有还是继续买入，并针对不同的投资情境（如短期与长期）提出具体的下一步行动建议（如是否应调整仓位、关注其他市场趋势）。"
            f"在分析中请考虑当前的市场环境和经济形势。总结部分请至少300字，并结合上述分析给出整体投资建议，使用繁体中文回答：\n\n{analysis_text}"
        )
        response = model.generate_content(contents=[full_prompt])
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        return f"无法生成报告: {e}"


# 主程序
def main() -> None:
    result = analyze_stock(ticker, buy_price)
    if result:
        if "aum" in result:  # 如果分析结果中包含 AUM，则表示是 ETF 分析
            analysis_text = format_etf_analysis_text(result)
        else:
            analysis_text = format_analysis_text(result)

        while True:  # 无限循环，直到用户输入正确
            api = input(
                "请选择生成报告的 API 服务 \n1: ChatGPT\n2: Gemini API\n其他: 不生成报告\n请输入: "
            )
            if api == "1":
                if client.api_key:
                    openai_analysis = generate_stock_analysis_with_chatgpt(
                        client, analysis_text
                    )
                    full_report = (
                        (
                            f"{analysis_text}\n\n"
                            f"ChatGPT 生成的分析报告:\n{openai_analysis}"
                        )
                        if openai_analysis  # 刚刚这个值是None，bool(None) == False
                        else "无法生成 ChatGPT 分析报告。"
                    )
                    break
                else:
                    full_report = f"无法生成 ChatGPT 分析报告，因为 API 密钥缺失。\n{analysis_text}"
                    break
            elif api == "2":
                if api_key:
                    gemini_analysis = generate_stock_analysis_with_gemini(
                        api_key, analysis_text
                    )
                    full_report = (
                        (
                            f"{analysis_text}\n\n"
                            f"Gemini API 生成的分析报告:\n{gemini_analysis}"
                        )
                        if gemini_analysis
                        else "无法生成 Gemini 分析报告。"
                    )
                    break
                else:
                    full_report = f"无法生成 Gemini 分析报告，因为 API 密钥缺失。\n{analysis_text}"
                    break
            else:
                print("输入错误，请重新输入。")
        print(full_report)


if __name__ == "__main__":
    main()
