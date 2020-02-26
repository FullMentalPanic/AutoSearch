import os
import subprocess
import requests
import re
from bs4 import BeautifulSoup

try:
    from urllib.parse import quote
except ImportError:
    from urllib import pathname2url as quote

DEBUG = 1

class dmhy_search(object):
    domain = "https://share.dmhy.org"
    search_link="https://share.dmhy.org/topics/list?keyword="
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

    def __init__(self, keyword= str()):
        self.search_list_info = []
        self.search_list_magent = []
        self.word = keyword

    def run(self):
        key = quote(self.word)
        url = self.search_link + key
        self.extract_info(url)
        print (self.search_list_info)

    def extract_info(self,url):
        count = 0
        while count < 2:
            res=requests.get(url)
            bs=BeautifulSoup(res.text,"html.parser")
            result = bs.find_all("div", class_="table clear")
            animate_infos = result[0].find("tbody")
            if animate_infos is None:
                return
            animate = animate_infos.find_all("tr", class_="")
            for link in animate:
                tmp = link.find("td", "title")
                title = (tmp.find("a", target="_blank")).text.strip()
                tmp = link.find_all("td", nowrap="nowrap")
                magent = (tmp[0].a).get('href') #magent
                size = tmp[1].text.strip() #size
                seed = tmp[2].text.strip() # seed
                finished = tmp[3].text.strip() # finished
                info = title + '+'+size+'+'+seed+'+'+finished
                self.search_list_info.append(info)
                self.search_list_magent.append(magent)

            change_page = result[0].find("div", class_= "fl")
            page_links = change_page.find_all("a")
            if len(page_links) < 1:
                return
            if len(page_links) < 2:
                count = count + 1
            next_page = page_links[-1].get('href')
            url = self.domain + next_page


if DEBUG == 1:
    test = dmhy_search("宝石商人理查德的谜鉴定")
    test.run()