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

    def __init__(self):
        self.group = {0:"動畫",1:"季度全集",2:"ＲＡＷ",3:"漫畫"}
        jieba.load_userdict('dict.txt') 

    def run(self, keyword: str, episode:int, class_num = 0,min_time = datetime(2018, 9, 1, 0, 0), basepattern = ''):
        search_class = self.group[class_num]
        key = quote(keyword)
        episodes= []
        self.basepattern = basepattern
        for i in range(episode,episode + 20):
            episodes.append(i)


        result = self.extract_info(key,episodes,search_class,min_time)

        #if len(result) == 0:
        #    smallword = keyword.split(' ')
        #    longest_string = max(smallword, key=len)
        #    key = quote(longest_string)
        #    result = self.extract_info(key,episodes,search_class,min_time)

        torrents = []
        nextepisode = episode
        finalbasepattern = basepattern
        if len(result) != 0:
            temp = False
            for i in range(episode,episode + 20):
                if i in result:
                    torrents.append(result[i][0])
                    nextepisode = i
                    finalbasepattern = result[i][1]
                    temp = True
                else:
                    break
            if temp:
                nextepisode +=1

        return nextepisode,finalbasepattern,torrents


    def extract_info(self, key: str, episodes:list(), search_class:str, min_time=datetime(2018, 9, 1, 0, 0),basepattern = ''):
        url = self.search_link + key
        animatelist = dict()
        res=requests.get(url)
        bs=BeautifulSoup(res.text,"html.parser")
        result = bs.find_all("item")
        mybasepattern = basepattern
        for link in result:
            dnd_time = (link.find("pubdate").text)[5:16]
            dnd_time=datetime.strptime(dnd_time, '%d %b %Y')
            title = (link.find("title")).text
            Web_class = (link.find("category")).text
            if Web_class == search_class and dnd_time > min_time:
                
                tmp = link.find("enclosure")
                magent = tmp.get('url') #magent
                seg_list = jieba.cut(title, HMM=True)
                #print (", ".join(seg_list))
                for item in seg_list: 
                    try:
                        temp = int(item)
                    except:
                        temp = item
                    if temp in episodes:                        
                        if temp in animatelist:
                            current_ratio = self.string_similar(mybasepattern,title)
                            max_ratio = animatelist[temp][2]
                            if current_ratio > max_ratio:
                                mybasepattern = title
                                info = [magent,mybasepattern,current_ratio]
                                animatelist.update({temp:info})
                        else:
                            if mybasepattern == '':
                                mybasepattern = title
                            max_ratio = self.string_similar(mybasepattern,title)
                            info = [magent,mybasepattern,max_ratio]
                            animatelist[temp] = info

        return animatelist

    def string_similar(self,basepattern,input_str = str()):
        return difflib.SequenceMatcher(None, basepattern, input_str).quick_ratio()







if DEBUG == 1:
    test = dmhy_search()
    print(test.run("2 43 清陰高中男子排球社",1, basepattern = ''))#海贼王 905 923
