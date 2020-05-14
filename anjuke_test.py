#!/usr/bin/env python3

import time
import requests
import random
#import pymysql
from parsel import Selector
from lxml import etree
import pandas as pd
from datetime import date


class AnJuKe():
    # 初始化
    def __init__(self, url, type):
#        self.connect = pymysql.connect(
#            host='localhost',
#            db='pachong',
#            user='root',
#            password='12345'
#        )
        #self.cursor = self.connect.cursor()  # 创建游标
        self.type  = type
        self.nj_loupan_anjuke = pd.DataFrame(columns=['Title', 'Location', 'Huxing', 'Tags', "Prices"])
        self.nj_ershoufang_anjuke = pd.DataFrame(columns=['Title', 'Location', 'Details', 'Tags', "Prices"])
        self.tree = self.get_tree(url)
        self.get_data()
        self.save_data()


    # 判断是否为空
    def is_empty(self, data):
        if data:
            data = data[0]
        else:
            data = '无信息'
        return data

    # 得到tree
    def get_tree(self, url):
        # 代理ip
        proxies_list = [{'http': 'http://117.191.11.111:8080'},
                        {'http': 'http://118.25.104.254:1080'},
                        {'http': 'http://203.195.168.154:3128'},
                        {'http': 'http://117.191.11.75:80'},
                        {'http': 'http://117.191.11.72:80'}, ]

        proxies = random.choice(proxies_list)
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'}
        response = requests.get(url, headers=headers, proxies=proxies)
        print(response)
        #tree = etree.HTML(response)

        #wr = requests.get(url, headers=headers, stream=True)
        sel = Selector(response.text)
        return sel

    # 获取城市详情
    def get_data(self):
        if self.type == "loupan":
            self.get_loupan()
        else:
            self.get_ershoufang()



    def get_ershoufang(self):
        for i in range(1, 51):
            url = 'https://nanjing.anjuke.com/sale/p%s/' % (i)
            print(url)
            tree = self.get_tree(url)
            titles = tree.xpath('//div[@class="house-title"]/a[@title]/text()').extract()
            titles = [title.replace("\n","") for title in titles]
            #print(titles)
            details = tree.xpath('//div[@class="details-item"][1]').xpath('string(.)').extract()
            details = [detail.replace("\n","").replace(" ","") for detail in details]
            locations = tree.xpath('//div[@class="details-item"][2]').xpath('string(.)').extract()
            locations = [location.replace("\n", "").replace(" ", "") for location in locations]
            prices = tree.xpath('//div[@class="pro-price"]').xpath('string(.)').extract()
            prices = [price.replace("\n","").replace(" ","") for price in prices]
            tags = tree.xpath('//div[@class="tags-bottom"]').xpath('string(.)').extract()
            tags = [tag.replace("\n", "").replace(" ", "") for tag in tags]
            #print(tags)
            if len(prices) != len(titles) or len(tags) != len(titles) or len(details) != len(titles) or len(
                    locations) != len(titles):
                print("Warnning! Some item length do not match.")

            pages_info = pd.DataFrame(list(zip(titles, locations, details, tags, prices
                                               )),
                                      columns=['Title', 'Location', 'Details', 'Tags', "Prices"])
            #print(pages_info["Title"])

            self.nj_ershoufang_anjuke = pd.concat([self.nj_ershoufang_anjuke, pages_info], ignore_index=True)
            time.sleep(5)

    def get_loupan(self):
        # 城市列表
        city_list_class = self.tree.xpath(
            '//div[@class="letter_city"]/ul/li[position()>12 and position()<18]/div/a/@href')
        # https://nj.fang.anjuke.com/loupan/all/p1/
        #rint(city_list_class)

        for i in range(1, 21):

            # print(1)
            url = 'https://nj.fang.anjuke.com/loupan/all/p%s/' % (i)
            #url = '%s.zu.anjuke.com/fangyuan/p%s/' % (city_url1, i)
            print(url)
            # 调用get函数
            tree = self.get_tree(url)
            #wr = requests.get(url, headers=headers, stream=True)
            #sel = Selector(wr.text)
            #print(url)
            #title = []
            #list_mod = tree.xpath('//div[@class="key-list imglazyload"]')
            #print(list_mod)
            title = tree.xpath('//span[@class="items-name"]/text()').extract()
            #print(title)
            location = tree.xpath('//span[@class="list-map"]/text()').extract()
            print(len(location))
            huxing = tree.xpath('//a[@class="huxing" or @class="kp-time"]').xpath('string(.)').extract()
            huxing = [item.replace("\n","").replace("\t","").replace(" ","") for item in huxing]
            print(len(huxing))
            tags = tree.xpath('//div[@class="tag-panel"]').xpath('string(.)').extract()
            tags = [tag.replace("\n",",").replace(" ","") for tag in tags]
            print(len(tags))
            prices = tree.xpath('//a[@class="favor-pos"]').xpath('string(.)').extract()
            prices = [price.replace("\n","").replace(" ","") for price in prices]
            print(len(prices))
            if len(prices) != len(title) or len(tags) != len(title) or len(huxing) != len(title) or len(location) != len(title):
                print("Warnning! Some item length do not match.")
            
            pages_info = pd.DataFrame(list(zip(title, location, huxing, tags, prices
                                               )),
                                      columns=['Title', 'Location', 'Huxing', 'Tags', "Prices"])
            self.nj_loupan_anjuke = pd.concat([self.nj_loupan_anjuke, pages_info], ignore_index=True)
            time.sleep(5)


    def save_data(self):
        today = date.today()
        print("Today's date:", today)
        filename = '_'.join(["nanjing", self.type,"anjuke", str(today)]) + ".xlsx"
        dir = "d:/HousePrice"
        if self.type == "loupan":
            self.nj_loupan_anjuke.to_excel('/'.join([dir, filename]))
        else:
            self.nj_ershoufang_anjuke.to_excel('/'.join([dir, filename]))

    # 保存数据库
#    def save_mysql(self, title, image, bedroom_num, living_room_num, area, floor, floors, agent, neighborhood, addres,
#                   rent_way, face_direction, subline, price):
#        sql = 'insert into anjuke(title,image,bedroom_num,living_room_num,area,floor,floors,agent,neighborhood,addres,rent_way,face_direction,subline,price) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
#        self.cursor.execute(sql, (
#        title, image, bedroom_num, living_room_num, area, floor, floors, agent, neighborhood, addres, rent_way,
#        face_direction, subline, price))
#        self.connect.commit()
#        print('数据插入成功')

        # except:
        #     print('数据插入失败')

    # 自创字符转码
    def zhuanma(self, mm):
        str1 = ''
        dicts = {'驋': '1', '餼': '2', '龤': '3', '麣': '4', '鑶': '5', '齤': '6', '鸺': '7', '閏': '8', '龥': '9', '龒': '0',
                 '.': '.'}
        for i in mm:
            if i in dicts:
                ss = dicts[i]
                str1 += ss
            else:
                str1 += i
        return str1


if __name__ == '__main__':
    url = 'https://www.anjuke.com/sy-city.html'
    AnJuKe(url, "ershoufang")