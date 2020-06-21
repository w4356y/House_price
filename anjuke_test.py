# -*- coding: utf-8 -*-
# @Time    : 6/21/2020 2:55 PM
# @Author  : Wei Jiang
# @FileName: anjuke_test.py
# @Software: PyCharm
# @Github  : https://github.com/w4356y/House_price.git
import time
import requests
import random
#import pymysql
from parsel import Selector
from lxml import etree
import pandas as pd
from datetime import date

## 定义class
class AnJuKe():
    # 初始化
    def __init__(self, url, type):
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
        sel = Selector(response.text)
        return sel

    ## 调用相应爬取函数
    def get_data(self):
        if self.type == "loupan":
            self.get_loupan()
        else:
            self.get_ershoufang()


    ## 爬取二手房信息
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
    ## 爬取新房信息
    def get_loupan(self):
        for i in range(1, 21):

            # print(1)
            url = 'https://nj.fang.anjuke.com/loupan/all/p%s/' % (i)
            #url = '%s.zu.anjuke.com/fangyuan/p%s/' % (city_url1, i)
            print(url)
            # 调用get函数
            tree = self.get_tree(url)
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

    ## 保存数据
    def save_data(self):
        today = date.today()
        print("Today's date:", today)
        filename = '_'.join(["nanjing", self.type,"anjuke", str(today)]) + ".xlsx"
        dir = "d:/HousePrice"
        if self.type == "loupan":
            self.nj_loupan_anjuke.to_excel('/'.join([dir, filename]))
        else:
            self.nj_ershoufang_anjuke.to_excel('/'.join([dir, filename]))



if __name__ == '__main__':
    url = 'https://www.anjuke.com/sy-city.html'
    AnJuKe(url, "ershoufang")