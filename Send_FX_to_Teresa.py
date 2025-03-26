# load package
from google_currency import convert
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import json
import os
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import yfinance as yf
from datetime import datetime, timedelta

def get_stock_data(symbol, days=30):
    """Get stock data for given symbol and days"""
    end_date = datetime.now()
    start_date = end_date  - timedelta(days=days)
    try:
        stock = yf.Ticker(symbol)
        print(stock.info)
        df = stock.history(start=start_date, end=end_date)
        return df
    except:
        return None


####test update

# google currency
def get_google_currency(source_currency, target_currency):
    url = f"https://www.google.com/search?q={source_currency}+{target_currency}"
    url = f"https://www.google.com/finance/quote/{source_currency}-{target_currency}"
    # print(f'{url}')
    User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    Headers = {'User-Agent' : User_Agent}
    response = requests.get(url, headers=Headers)
    # print(f'status_code: {response.status_code}')
    # print(f'TEST: {response.text}')
    # test = BeautifulSoup(response.text, 'lxml').get_text()
    # print(f'RESULT: {test}')
    # return BeautifulSoup(response.text, 'lxml').find("div", class_="BNeawe iBp4i AP7Wnd").get_text().split(' ')[0]
    return BeautifulSoup(response.text, 'lxml').find("div", class_="YMlKec fxKbKc").get_text().split(' ')[0]


# usd_to_jpy = get_google_currency('USD', 'JPY')
# usd_to_ntd = get_google_currency('USD', 'TWD')
# ntd_to_jpy = get_google_currency('TWD', 'JPY')
# print(f'USD2JPN:{usd_to_jpy}, USD2NTD:{usd_to_ntd}, NTD2JPY:{ntd_to_jpy}')
# google currency




# r = requests.get('https://www.cathaybk.com.tw/cathaybk/personal/product/deposit/currency-billboard')
# r2 = requests.get("https://fubon-ebrokerdj.fbs.com.tw/Z/ZM/ZMJ/ZMJ.djhtm")
# cathay_usd = float(BeautifulSoup(r.text, "lxml").find_all('tr')[1].find_all('td')[2].find('div').text)
# test_str = BeautifulSoup(r.text, "lxml").find_all('tr')
# # print(f'CATHAY:: {test_str}')
# stock_info = BeautifulSoup(r2.text, "lxml") #.find('td', class_="t3n1")
# data = stock_info.select('table')[0]
# # data = stock_info.select('table')
# print(data)
# print(f'STOCK:: {stock_info}')

# send message
def lineNotifyMessage(token, msg):
    r = requests.post(
        "https://notify-api.line.me/api/notify",
        headers={"Authorization": f"Bearer {token}"},
        data={"message": msg}
    )
    return r.status_code

# wrap_up
# message =(
#     # f'\n國泰美金兌台幣: {cathay_usd:.2f}\n\n'
#     f'USD_to_JPY: {usd_to_jpy}\n'
#     f'USD to_NTD: {usd_to_ntd}\n'
#     f'NTD to JPY: {ntd_to_jpy}\n'
#     'source: Google currency'
# )
# token = os.environ['LINE_NOTIFY_TOKEN']
# token = "JrCGTvWflGonpHV3kR498NHXNMwZlyR7FOHJKM7cDaW"
# token = "hIWcMyy4bQsWiW+euigdcKuKOmErY38hotg5DHC5j+eYoU3a/9U7nPcwfPD437EmLfDyB8SK3TOWqy4VBsdq8dA0xZeYvjpenF8ZR/katKoGlB7GMrsXo+lJ2CA3jrxfHeQbvBhaZDb29ZrghM2M1AdB04t89/1O/w1cDnyilFU="
# lineNotifyMessage(token, message)



def sendMSGtoClient(token, message, user_id):
    line_bot_api = LineBotApi(token)
    message = TextSendMessage(text=message)
    line_bot_api.push_message(to = user_id, messages=message)

def composeMSG ():
    usd_to_jpy = get_google_currency('USD', 'JPY')
    usd_to_ntd = get_google_currency('USD', 'TWD')
    ntd_to_jpy = get_google_currency('TWD', 'JPY')
    message =(
    f'USD_to_JPY: {usd_to_jpy}\n'
    f'USD to_NTD: {usd_to_ntd}\n'
    f'NTD to JPY: {ntd_to_jpy}\n'
    'source: Google finanace')
    return message

def stock_price_gen(symbol):
    # symbol = symbol+".tw"
    symbol = symbol
    ticker =  yf.Ticker(symbol)
    info = ticker.info
    # stock_df = get_stock_data(symbol,0)
    # close_p = stock_df["Close"][0]
    # open_p = stock_df["Open"][0]
    # high_p = stock_df["High"][0]
    # low_p = stock_df["Low"][0]
    name = info["shortName"]
    current_p = info["regularMarketPrice"]
    close_p = ticker.info["regularMarketPreviousClose"]
    open_p = ticker.info["regularMarketOpen"]
    high_p = ticker.info["regularMarketDayHigh"]
    low_p = ticker.info["regularMarketDayLow"]
    # print(stock_df)
    msg = (
    f'\n股價代碼為: {symbol}\n'
    f'\n名稱: {name}\n\n'
    f'現價: {current_p}\n'
    f'收盤價: {close_p}\n'
    f'開盤價: {open_p}\n'
    f'最高: {high_p}\n'
    f'最低: {low_p}\n'
    )
    return msg


if __name__ == "__main__":
    token = "hIWcMyy4bQsWiW+euigdcKuKOmErY38hotg5DHC5j+eYoU3a/9U7nPcwfPD437EmLfDyB8SK3TOWqy4VBsdq8dA0xZeYvjpenF8ZR/katKoGlB7GMrsXo+lJ2CA3jrxfHeQbvBhaZDb29ZrghM2M1AdB04t89/1O/w1cDnyilFU="
    # 設定你的Channel Access Token
    channel_access_token = token
    # 創建Line Bot API物件
    line_bot_api = LineBotApi(channel_access_token)
    # 用戶ID，這是你想要發送訊息的用戶
    user_id = "U7ba3afa719a7755f1ae6d896d6073902" #Paul
    # user_id = "Udde268c97307d903ece6a97a93743ad5" #shao

    message = composeMSG()
    # 要發送的訊息
    message = TextSendMessage(text=message)

    # 發送訊息
    # line_bot_api.push_message(to = user_id, messages=message)

    ###STOCK QUERY
    msg = stock_price_gen("2330.tw")
    print(f"STOCK: {msg}")
