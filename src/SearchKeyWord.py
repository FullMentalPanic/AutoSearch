# -*- coding: utf-8 -*-
#this file is to find torrent to download, use jieba to find episode and format 

import os
import subprocess
import requests
import re
from bs4 import BeautifulSoup
import jieba
from datetime import datetime
import difflib

try:
    from urllib.parse import quote
except ImportError:
    from urllib import pathname2url as quote

DEBUG = 0

class dmhy_search(object):
    domain = "https://share.dmhy.org"
    search_link="https://share.dmhy.org/topics/rss/rss.xml?keyword="
    header={
       "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
       "Accept-Encoding":"gzip, deflate",
       "Accept-Language":"zh-CN,zh;q=0.8",
       "Cache-Control":"max-age=0",
       "Connection":"keep-alive",
       "Content-Length":"65",
       "Content-Type":"application/x-www-form-urlencoded",
       "Host":"btkitty.bid",
       "Origin":"blog.aipanpan.com",
       "Referer":"blog.aipanpan.com",
       "Upgrade-Insecure-Requests":"1",
       "User-Agent":"Mozilla/5.0 (Windows NT 10.0.14393; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2950.5 Safari/537.36"
       }

    def __init__(self, keyword= str(), episodes = list, class_num = 0,min_time = datetime(2018, 9, 1, 0, 0), basepattern = ''):
        self.search_list_info = dict() # title , seed, finish, magent
        self.search_list_magent = []
        self.number = episodes
        group = {0:"動畫",1:"季度全集",2:"ＲＡＷ",3:"漫畫"}
        self.search_class = group[class_num]
        key = quote(keyword)
        self.url = self.search_link + key
        self.min_time = min_time
        self.basepattern = basepattern
        for num in self.number:
            self.search_list_info[num] = []
        jieba.load_userdict('dict.txt') 

    def run(self):       
        self.extract_info()
        self.sort_hot_resource()
        return(self.search_list_magent)
       

    def extract_info(self):
        url = self.url 
        res=requests.get(url)
        bs=BeautifulSoup(res.text,"html.parser")
        result = bs.find_all("item")
        for link in result:
            dnd_time = (link.find("pubdate").text)[5:16]
            dnd_time=datetime.strptime(dnd_time, '%d %b %Y')
            title = (link.find("title")).text
            Web_class = (link.find("category")).text
            if Web_class == self.search_class and dnd_time > self.min_time:
                tmp = link.find("enclosure")
                magent = tmp.get('url') #magent
                seg_list = jieba.cut(title, HMM=True)
                #print (", ".join(seg_list))
                for item in seg_list: 
                    try:
                        temp = int(item)
                    except:
                        temp = item
                    if temp in self.number:
                        info = [title,magent] 
                        self.search_list_info[temp].append(info)


    def sort_hot_resource(self):
        for key in self.search_list_info:
            temp_list = self.search_list_info[key]
            #print (temp_list)
            if len(temp_list) is not  0:
                if self.basepattern is '':
                    #temp_list.sort(key=lambda x: (x[1], x[2]))
                    self.search_list_magent.append(temp_list[-1])
                else:
                    max_ratio = 0
                    result = []
                    for item in temp_list:
                        ratio = self.string_similar(item[0])
                        if ratio > max_ratio:
                            max_ratio = ratio
                            result = item
                    print("max tratio is {}".format(max_ratio))
                    self.search_list_magent.append(result)


    def string_similar(self,input_str = str()):
        return difflib.SequenceMatcher(None, self.basepattern, input_str).quick_ratio()







if DEBUG == 1:
    test = dmhy_search("刀剑神域 Alicization War of Underworld",[3], basepattern = '[c.c動漫][10月新番][刀劍神域 Alicization War of Underworld][01][BIG5][1080P][MP4][網盤]')
    print (test.run())#海贼王 905 923
