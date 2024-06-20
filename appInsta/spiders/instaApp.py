import scrapy
import json
import csv
from pprint import pprint
import random
from .user_agents import user_agents

class InstApp(scrapy.Spider):
    name = 'insta'

    hashtag = 'chillipowder'
    
    user_list = []
    c = 0
    def __init__(self, hashtag=None):
        if hashtag:
            self.hashtag = hashtag

        filename = 'tag_users_' + self.hashtag +'.csv'
        output_file = open(filename, 'w')
        columns = ['hashtag','username','fullname','user_id']
        self.writer = csv.writer(output_file)
        self.writer.writerow(columns)

    def start_requests(self):
        self.url = f"https://i.instagram.com/api/v1/feed/tag/{self.hashtag}/"

        ua = random.choice(user_agents)
        self.headers = {
          # 'Accept' : '*/*',
          # 'Accept-Encoding' : 'gzip, deflate, br',
          # 'Connection' : 'keep-alive',
          # 'Cookie': 'mid=YHApkgAEAAHvaFfEUzmjvaivJrV9; ig_did=A278B6B4-C385-4486-998B-7D6BCDE8FF99; ig_nrcb=1; shbid=17475; shbts=1620643624.4130502; rur=PRN; csrftoken=9VyH0svcI3t9u8yhsxDc4zA3L3UGwnmy; ds_user_id=3430001010; sessionid=3430001010%3Aa6dv7E8cNJySB8%3A23',
          'Content-Type': 'application/json; charset=utf-8',
          # 'User-Agent': 'Instagram 146.0.0.27.125 Android (23/6.0.1; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US',
          'User-Agent' : ua,
          'Host' : 'i.instagram.com',
        }
        Cookie = {
            'sessionid' : '3430001010%3AMqMBB1Ykta2abM%3A9%3AAYf6qLKYDSurNJ3ZQVO52w_7ouD4f7kPp-A5fJPcyw'
        }

        yield scrapy.Request(self.url, headers=self.headers, cookies=Cookie, meta={'cookiejar': '1'},callback=self.parse)

    def parse(self, response):
        json_data = json.loads(response.body)
        for item in json_data['items']:
            if not item:
                print("No item found!!")
                continue
            try:
                user = item.get('caption').get('user')
                caption = item.get('caption').get('text')
                post_url = item.get('image_versions2').get('candidates')[0].get('url')
            except Exception as e:
                print(e)
                user = None
                continue
            # pprint(user)
            if not user:
                print("no user found!! below is post structure - ")
                pprint(item)
                continue
            username = user['username']
            full_name = user['full_name']
            user_id = user['pk']
            profile_pic_url = user['profile_pic_url']
            post_url = post_url
            caption = caption

            if user_id not in self.user_list:
                self.user_list.append(user_id)
                row = [self.hashtag, username, full_name, user_id,profile_pic_url,caption]
                self.writer.writerow(row)
                self.c += 1
                print(self.c, row)

            else:
                print(username, 'user already exists!!')

        if json_data.get('more_available'):
            print("Next page available")
            Cookie = {
                'sessionid' : '3430001010%3AMqMBB1Ykta2abM%3A9%3AAYf6qLKYDSurNJ3ZQVO52w_7ouD4f7kPp-A5fJPcyw'
            }
            next_max_id = json_data.get('next_max_id')
            print("Next max id is:", next_max_id)
            url = self.url + "?max_id=" + next_max_id
            yield scrapy.Request(url, headers=self.headers, dont_filter=True ,meta={'cookiejar': response.meta.get('cookiejar')}, callback=self.parse)
        else:
            del json_data['items']
            pprint(json_data)
