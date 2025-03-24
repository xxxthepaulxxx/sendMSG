# load package
from google_currency import convert
from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
import os
import streamlit as st

# # get data
# usd_to_jpy = json.loads(convert('usd', 'jpy', 1))['amount']
# usd_to_ntd = json.loads(convert('usd', 'twd', 1))['amount']
# ntd_to_jpy = json.loads(convert('twd', 'jpy', 1))['amount']

####test thupdate


# google currency
def get_google_currency(source_currency, target_currency):
    url = f"https://www.google.com/search?q={source_currency}+to+{target_currency}"
    response = requests.get(url)
    return BeautifulSoup(response.text, 'lxml').find("div", class_="BNeawe iBp4i AP7Wnd").get_text().split(' ')[0]


# r = requests.get('https://www.cathaybk.com.tw/cathaybk/personal/product/deposit/currency-billboard')
# cathay_usd = float(BeautifulSoup(r.text, "lxml").find_all('tr')[1].find_all('td')[2].find('div').text)

uu = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
r3 = requests.get(uu)
r2 = requests.get("https://fubon-ebrokerdj.fbs.com.tw/Z/ZM/ZMJ/ZMJ.djhtm")

# test_str = BeautifulSoup(r2.text, "lxml").find_all('tr')
soup = BeautifulSoup(r3.text, "lxml") 
tr = soup.findAll('tr')
tds = []
for raw in tr:
     data = [td.get_text() for td in raw.findAll("td")]
     if len(data) == 7:
         tds.append(data)


df = pd.DataFrame(tds[1:],columns=tds[0])
st.dataframe(df)
# st.selectbox("aaaa",df['代號及名稱'])
st.write("Hello Paul")

# print(tr)
# print(test_str)


# print(f'STOCK:: {stock_info}')

# send message
def lineNotifyMessage(token, msg):
    r = requests.post(
        "https://notify-api.line.me/api/notify",
        headers={"Authorization": f"Bearer {token}"},
        data={"message": msg}
    )
    return r.status_code

