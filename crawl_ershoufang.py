# -*- coding: utf-8 -*-
# @Time    : 6/21/2020 2:55 PM
# @Author  : Wei Jiang
# @FileName: crawl_ershoufang.py
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
爬取链家南京二手房信息
@time="202005"
@author="Wei Jiang"
'''

###########################################################
# 进行网络请求的浏览器头部
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 BIDUBrowser/8.7 Safari/537.36'

}
# pages是不同页码的网址列表,由于网页只显示前100页
pages = ['https://nj.lianjia.com/ershoufang/jiangning/pg{}/'.format(x) for x in range(1, 101)]
############################################################

#############################################################
## 输出数据框列名
lj_futian = pd.DataFrame(columns=['Title', 'Position1', 'Position2',
                                  'HouseInfo',"FollowInfo","Tags",
                                  "Total_Price","Unit_Price"]
                         )

count = 0

## 提取页码最大数字
def get_maxPage(url):
    wr = requests.get(url, headers=headers, stream=True)
    sel = Selector(wr.text)
    pages = sel.xpath('//div[@class="page-box"]/@data-total-count').extract()
    print('Total new house:' + pages[0])
    n_page = (int(pages[0]) // 10) + 1
    return(n_page)

## 根据城市名称和房源类型以及时间生成相应文件
def get_outFile(city, type):
    today = date.today()
    print("Today's date:", today)
    filename = '_'.join([city,type,str(today)]) + ".xlsx"
    return(filename)

## 解析网页数据
def l_par_html(url):
    # 这个函数是用来获取链家网南京二手房的信息
    wr = requests.get(url, headers=headers, stream=True)
    sel = Selector(wr.text)
    h_test = sel.xpath('//h2[@class="total fl"]').extract()
    title = sel.xpath('//li//div//div[@class="title"]/a/text()').extract()
    pos1 = sel.xpath('//li//div//div[@class="flood"]//div/a[@data-el="region"]/text()').extract()
    pos2 = sel.xpath('//li//div//div[@class="flood"]//div/a[2]/text()').extract()
    houseInfo = sel.xpath('//li//div//div[@class="address"]//div/text()').extract()
    followInfo = sel.xpath('//li//div//div[@class="followInfo"]/text()').extract()
    tags = sel.xpath('//li//div//div[@class="tag"]').xpath('string(.)').extract()
    # print(tags)
    #tag_taxfree = sel.xpath('//li//div//div[@class="tag"]/span[@class="taxfree"]/text()').extract()
    #tag_haskey = sel.xpath('//li//div//div[@class="tag"]/span[@class="haskey"]/text()').extract()
    total_price = sel.xpath('//li//div//div[@class="priceInfo"]//div[@class="totalPrice"]//span/text()').extract()
    unit_price = sel.xpath('//li//div//div[@class="priceInfo"]//div[@class="unitPrice"]//span/text()').extract()
    if  len(total_price) != len(title)  or \
            len(tags) != len(title) or len(followInfo) != len(title) or len(houseInfo) != len(title) or \
            len(pos1) != len(title) or len(pos2) != len(title):
        print("Warnings! Length of some item does not match.")
    #print(len(tags))
    pages_info = pd.DataFrame(list(zip(title, pos1, pos2,houseInfo,followInfo, tags, total_price,unit_price)),
                              columns=['Title', 'Position1', 'Position2','HouseInfo',"FollowInfo","Tags","Total_Price","Unit_Price"])
    return pages_info

if __name__ == "__main__":
    file = get_outFile(city="nanjing", type="ershoufang_jiangning")
    dir = "d:/HousePrice"
    print(file)
    for page in pages:
        a = l_par_html(page)
        #print(a)
        count = count + 1
        print('the ' + str(count) + ' page is sucessful')
        time.sleep(5)
        lj_futian = pd.concat([lj_futian, a], ignore_index=True)

# 将表格数据输出到excel文件
    lj_futian.to_excel('/'.join([dir,file]))