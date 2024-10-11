# load package
from google_currency import convert
from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
import os

# get data
usd_to_jpy = json.loads(convert('usd', 'jpy', 1))['amount']
usd_to_ntd = json.loads(convert('usd', 'twd', 1))['amount']
ntd_to_jpy = json.loads(convert('twd', 'jpy', 1))['amount']

r = requests.get('https://www.cathaybk.com.tw/cathaybk/personal/product/deposit/currency-billboard')
cathay_usd = float(BeautifulSoup(r.text, "lxml").find_all('tr')[1].find_all('td')[2].find('div').text)

# send message
def lineNotifyMessage(token, msg):
    r = requests.post(
        "https://notify-api.line.me/api/notify",
        headers={"Authorization": f"Bearer {token}"},
        data={"message": msg}
    )
    return r.status_code

# wrap_up
message =(
    f'\n國泰美金兌台幣: {cathay_usd:.2f}\n\n'
    f'USD to JPY: {usd_to_jpy}\n'
    f'USD to NTD: {usd_to_ntd}\n'
    f'NTD to JPY: {ntd_to_jpy}\n'
    'source: Google currency'
)
token = os.environ['LINE_NOTIFY_TOKEN']
lineNotifyMessage(token, message)
