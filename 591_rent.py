from bs4 import BeautifulSoup
import requests
from datetime import timedelta
import random
import time
import re

import os

class Rent591Watcher:
    def __init__(self, url:str, token:str, wanted_page:int=2):
        self.headers={
            'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
            }
        self.search_url = f"{url.replace('sort=posttime_desc', '')}&sort=posttime_desc"
        self.__linetoken=token
        self.wanted_page = wanted_page
    
    def get_house_id(self):
        
        # get token
        s = requests.Session()
        url = 'https://rent.591.com.tw/'
        r = s.get(url, headers=self.headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        token = soup.find('meta', attrs={'name': 'csrf-token'})
        headers = self.headers.copy()
        headers['X-CSRF-TOKEN'] = token

        # search
        house_ids = []
        page = 1
        while page <= self.wanted_page:
            url = self.search_url if page <2 else f'{self.search_url}&page={page}'
            r = s.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            house_ids += [i.get('href').split('/')[-1] for i in soup.find_all(class_="link v-middle")]
            page +=1
            time.sleep(random.uniform(1, 3))

        print(f'get {len(house_ids)} ids')
        return house_ids

    def get_house_detail(self, house_id):
        headers = self.headers.copy()
        
        s = requests.Session()
        url = f'https://rent.591.com.tw/{house_id}'
        r = s.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        token = soup.find('meta', attrs={'name': 'csrf-token'})

        headers = headers.copy()
        headers['X-CSRF-TOKEN'] = token
        headers['deviceid'] = s.cookies.get_dict()['T591_TOKEN']
        # headers['token'] = s.cookies.get_dict()['PHPSESSID']
        headers['device'] = 'pc'

        url = f'https://bff.591.com.tw/v1/house/rent/detail?id={house_id}'
        r = s.get(url, headers=headers)
        house_detail = r.json()['data']
        time.sleep(random.uniform(1, 3))
        print(f'get {house_id} detail')
        return house_detail
    
    def generate_message(self, id, house_detail):
        house_type = house_detail.get('favData').get('kindTxt')
        price = f"{house_detail.get('favData').get('price'):,.0f}"
        area = f"{house_detail.get('favData').get('area')}坪"
        floor = house_detail.get('info')[2].get('value') if len(house_detail.get('info')) > 2 else None
        shape = house_detail.get('gtm_detail_data').get('shape_name')
        address = house_detail.get('favData').get('address').replace('台北市', '')
        post_time = house_detail.get('publish').get('postTime').replace('此房屋在', '')
        update_time = house_detail.get('publish').get('updateTime') #if len(house_detail.get('publish').get('updateTime'))>0 else '-'
        time_ = f"{post_time}{' | ' + update_time if update_time else ''}"
        note = house_detail.get('favData').get('other').get('desc')
        link = f'https://rent.591.com.tw/{id}'
        
        return (f"\n{house_type} | {price} \n{area} | {floor} | {shape}\n{address}\n{time_}\n*{note}\n{link}")

    def transform_post_time(self, post_time):
        post_time = post_time.replace('此房屋在', '').replace('前發佈', '')
        if '秒鐘' in post_time:
            seconds_ago = int(re.search(r'(\d+)秒鐘', post_time).group(1))
            return timedelta(seconds=seconds_ago)
        elif '分鐘' in post_time:
            minutes_ago = int(re.search(r'(\d+)分鐘', post_time).group(1))
            return timedelta(minutes=minutes_ago)
        elif '小時' in post_time:
            hours_ago = int(re.search(r'(\d+)小時', post_time).group(1))
            return timedelta(hours=hours_ago)
        elif '天' in post_time:
            days_ago = int(re.search(r'(\d+)天', post_time).group(1))
            return timedelta(days=days_ago)
        else:
            return timedelta(0)

    def send_message(self, msg):
        headers = {
            "Authorization": f"Bearer {self.__linetoken}",
            "Content-Type" : "application/x-www-form-urlencoded"
            }
        payload = {'message': msg}
        r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
        return r.status_code
    
    def send_new_houses(self):
        house_ids = self.get_house_id()
        for id in house_ids:
            house_detail = self.get_house_detail(id)
            
            # check time
            post_time = house_detail.get('publish').get('postTime')
            post_time = self.transform_post_time(post_time)
            if post_time <= timedelta(hours=8): # send if within 8 hours
                msg = self.generate_message(id, house_detail)
                self.send_message(msg)

# send news with keywords
url = os.environ['URL'] # 591 url
linetoken = os.environ['LINE_NOTIFY_TOKEN'] # line token
wanted_page = 2
bot = Rent591Watcher(url, linetoken, wanted_page)
bot.send_new_houses()