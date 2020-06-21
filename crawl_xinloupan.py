# -*- coding: utf-8 -*-
# @Time    : 6/21/2020 2:55 PM
# @Author  : Wei Jiang
# @FileName: crawl_xinloupan.py
# @Software: PyCharm
# @Github  : https://github.com/w4356y/House_price.git

from bs4 import BeautifulSoup
import re
import requests
from parsel import Selector
import pandas as pd
import time
from datetime import date

#############################################################
'''
爬取链家南京市新楼盘数据
@time="2020-05-10"
@author="Wei Jiang"
'''
###########################################################
# 进行网络请求的浏览器头部
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 BIDUBrowser/8.7 Safari/537.36'

}
# pages是不同页码的网址列表,由于网页只显示前100页
base_url = "https://nj.fang.lianjia.com/loupan"

############################################################
## 提取页码最大数字
def get_maxPage(url):
    wr = requests.get(url, headers=headers, stream=True)
    sel = Selector(wr.text)
    pages = sel.xpath('//div[@class="page-box"]/@data-total-count').extract()
    print('Total new house:' + pages[0])
    n_page = (int(pages[0]) // 10) + 1
    return(n_page)
    #print(pages)

#############################################################
## 输出数据框列名
nj_loupan = pd.DataFrame(columns=['Title', 'Type', 'Status','District',"Street",
                                       "Location","Room","Area","Tags",
                                       "Unit_Price","Total_Price"]
                         )

count = 0

## 根据城市名称和房源类型以及时间生成相应文件
def get_outFile(city, type):
    today = date.today()
    print("Today's date:", today)
    filename = '_'.join([city,type,str(today)]) + ".xlsx"
    return(filename)

## 解析网页数据
def l_par_html(url):
    # 这个函数是用来获取链家网南京新房的信息
    wr = requests.get(url, headers=headers, stream=True)
    sel = Selector(wr.text)
    print(url)
    title = sel.xpath('//ul/li/div/div[@class="resblock-name"]/a/text()').extract()
    type = sel.xpath('//ul/li/div/div[@class="resblock-name"]/span[@class="resblock-type"]/text()').extract()
    status = sel.xpath('//ul/li/div/div[@class="resblock-name"]/span[@class="sale-status"]/text()').extract()
    district  = sel.xpath('//ul/li/div/div[@class="resblock-location"]/span[1]/text()').extract()
    street = sel.xpath('//ul/li/div/div[@class="resblock-location"]/span[2]/text()').extract()
    location = sel.xpath('//ul/li/div/div[@class="resblock-location"]/a/text()').extract()
    #room = sel.xpath('//ul/li/div/a[@class="resblock-room"]/span').extract()
    room = sel.xpath('//a[@class="resblock-room"]').xpath('string(.)').extract()
    room = [item.replace("\n","").replace(" ","") for item in room]
    #room = [item.extract() for item in room_sel]
    #room2 = sel.xpath('//ul/li/div/a[@class="resblock-room"]/span[2]/text()').extract()
    areas = sel.xpath('//ul/li/div/div[@class="resblock-area"]').xpath('string(.)').extract()
    areas = [area.replace("\n","").replace(" ","") for area in areas]
    tags = sel.xpath('//ul/li/div/div[@class="resblock-tag"]').xpath('string(.)').extract()
    #print(tags)
    tags = [tag.replace(" ","").replace("\n"," ") for tag in tags]
    #print(tags)
    unit_price = sel.xpath('//ul/li/div/div[@class="resblock-price"]/div/span[@class="number"]/text()').extract()
    total_price = sel.xpath('//ul/li/div/div[@class="resblock-price"]').xpath('string(.)').extract()
    total_price = [price.replace("\n","").replace(" ","") for price in total_price]
    #print(unit_price)
    #print(title)
    #print(len(areas))
    if len(total_price) != len(title) or len(areas) != len(title) or len(tags) != len(title) or \
            len(unit_price) != len(title) or len(room) != len(title) or len(district) != len(title) or \
            len(street) != len(title) or len(location) != len(title):
        print("Warnings! Length of some item does not match.")
    pages_info = pd.DataFrame(list(zip(title, type, status, district, street,
                                       location, room, areas, tags,
                                       unit_price, total_price)),
                              columns=['Title', 'Type', 'Status','District',"Street",
                                       "Location","Room","Area","Tags",
                                       "Unit_Price","Total_Price"])
    return pages_info

if __name__ == "__main__":
    file = get_outFile(city="nanjing", type="xinloupan")
    dir = "d:/HousePrice"
    print(file)
    n_page = get_maxPage(base_url)
    pages = ['https://nj.fang.lianjia.com/loupan/pg{}/'.format(x) for x in range(1, (n_page + 1))]
    for page in pages:
        #print(page)
        a = l_par_html(page)
        # print(a)
        count = count + 1
        print('the ' + str(count) + ' page is sucessful')
        time.sleep(5)
        nj_loupan = pd.concat([nj_loupan, a], ignore_index=True)

    # 将表格数据输出到excel文件
    nj_loupan.to_excel('/'.join([dir,file]))
