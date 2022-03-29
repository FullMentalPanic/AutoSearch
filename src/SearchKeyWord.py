# -*- coding: utf-8 -*-
#this file is to find torrent to download, use jieba to find episode and format 
import requests
import re
from bs4 import BeautifulSoup
import jieba
from datetime import datetime
import difflib
import time
import re


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

    def run(self, keyword: str, episode:int, class_num = 0,min_time = datetime(2018, 9, 1, 0, 0), basepattern = '',HD = True):
        search_class = self.group[class_num]
        key = quote(keyword)
        episodes= []
        for i in range(episode,episode + 1):#only check 1 episode
            episodes.append(i)

        retry = 0
        torrents = []
        nextepisode = episode
        finalbasepattern = basepattern

        while retry < 3:
            try:
                result = self.extract_info(key,episodes,search_class,min_time, basepattern,HD = HD)
                #if DEBUG:
                #    for i in result:
                #        print(result[i][1])
                break
            except:
                raise
                time.sleep(10)
                print("can not extract_info from dmhy")
                retry +=1
        else:
            return nextepisode,finalbasepattern,torrents

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


    def extract_info(self, key: str, episodes:list(), search_class:str, min_time=datetime(2018, 9, 1, 0, 0),basepattern = '',HD = True):
        url = self.search_link + key
        animatelist = dict()
        res=requests.get(url)
        bs=BeautifulSoup(res.text,"html.parser")
        result = bs.find_all("item")
        mybasepattern = basepattern
        if basepattern == '':
            pattern_learn = True
            patterns = dict()
        else:
            pattern_learn = False

        temp = []
        for link in reversed(result):
            dnd_time = (link.find("pubdate").text)[5:16]
            dnd_time=datetime.strptime(dnd_time, '%d %b %Y')
            title = (link.find("title")).text
            Web_class = (link.find("category")).text
            if Web_class == search_class and dnd_time > min_time:
                
                tmp = link.find("enclosure")
                magent = tmp.get('url') #magent

                _match,episode_,re_string = self.match_string(title,HD = HD)
                #print(title)
                #print(re_string)
                if _match:

                    if re_string != '':
                        if pattern_learn:
                            if re_string in patterns:
                                patterns[re_string] =  patterns[re_string] + 1
                            else:
                                patterns[re_string] =  1
                            mybasepattern = re_string
                        if episode_[0] in episodes:
                            try:
                                m = re.search(mybasepattern, title)
                            except:
                                print('re failed')
                                continue
                            if m:
                                info = [magent,mybasepattern]
                                animatelist[episode_[0]] = info
                                episodes.remove(episode_[0])
                            else:
                                temp.append([episode_,magent,re_string])

                    else:
                        temp.append([episode_,magent,re_string])

        #find rest of episodes              
        if episodes != [] and temp != []:
            for backup in temp:
                nums  = backup[0]
                for num in nums:
                    if num in episodes:
                        episodes.remove(num)
                        animatelist[num] = [backup[1],backup[2]]
                if episodes == []:
                    break

        if pattern_learn:
            if len(patterns):
                max_key = max(patterns, key=patterns.get)
                #print(max_key)
                if len(animatelist):
                    last = max(animatelist)
                    animatelist[last][1] = max_key



        return animatelist

    def string_similar(self,basepattern,input_str = str()):
        return difflib.SequenceMatcher(None, basepattern, input_str).quick_ratio()

    def match_string(self,title, HD = True,support_4K = False):
        seg_list = jieba.cut(title, HMM=True)
        if HD:
            HD_result = False
        else:
            HD_result = True

        is_episode = False
        num_string = ''
        episode = []
        re_string = ''
        result = False
        single = True
        #print(title)

        for item in seg_list:
            if not support_4K and item in ['3840×2160', '3840 × 2160','2160p','2160P']:
                HD_result = False
                return  False,0,''

            if item.isnumeric():
                try:
                    temp = item          
                    start_index = title.find(temp)
                    end_index = start_index + len(temp)
                    if (title[start_index - 1] in ['[','第','【'] ) and (title[end_index] in [']','话','話','集','】']):
                        is_episode = True
                        num_string = title[start_index - 1] +temp + title[end_index]
                        
                        temp_string = num_string.replace('[','\[')
                        temp_string = temp_string.replace(']','\]')
                        num_string_re = temp_string.replace(temp,'\d+')

                        episode.append(int(temp))
                    elif title[end_index] in ['[', '【'] or (title[end_index] == ' ' and title[end_index + 1] in ['[', '【']):
                        is_episode = True
                        num_string = title[start_index - 1] +temp + title[end_index]
                        
                        temp_string = num_string.replace('[','\[')
                        temp_string = temp_string.replace(']','\]')
                        num_string_re = temp_string.replace(temp,'\d+')

                        episode.append(int(temp))
                    else:
                        re_rule = '\d+\-\d+'
                        m = re.search(re_rule, title)
                        if m:
                            is_episode = True
                            num_string = m[0]
                            mid = m[0].find('-')
                            start = int(m[0][0:mid])
                            end = int(m[0][mid+1:])
                            episode = [i for i in range(start,end+1)]
                            single = False
                except:
                    pass


            if HD and (item in ['1080P' ,'1920x1080','1080p']):
                HD_result = True
            
            if HD:
                if is_episode and HD_result:
                    break
            else:
                if is_episode:
                    break
        if HD:
            result = is_episode and HD_result
        else:
            result = is_episode

        if result and single:
            num_string = num_string.replace('[','\[')
            num_string = num_string.replace(']','\]')
            #num_string_re = num_string.replace(num_string,'\d+')

            re_string = title
            re_string = re_string.replace('/','\/')
            re_string = re_string.replace('\\','\\\\')
            re_string = re_string.replace('(','\(')
            re_string = re_string.replace(')','\)')
            re_string = re_string.replace('[','\[')
            re_string = re_string.replace(']','\]')
            re_string = re_string.replace('{','\{')
            re_string = re_string.replace('}','\}')
            re_string = re_string.replace('*','\*')
            re_string = re_string.replace('$','\$')
            re_string = re_string.replace('+','\+')
            re_string = re_string.replace('.','\.')
            re_string = re_string.replace('^','\^')
            re_string = re_string.replace('?','\?')
            re_string = re_string.replace(num_string,num_string_re)
        else:
            re_string = ''
        

        return result,episode,re_string

        
            
  

              






if DEBUG == 1:
    test = dmhy_search()
    nextepisode,finalbasepattern,torrents = test.run("转生成蜘蛛又怎样",1, basepattern = '')#海贼王 905 923
    print(finalbasepattern)
    for i in range(5):
        print ('')
    nextepisode,finalbasepattern,torrents = test.run("转生成蜘蛛又怎样",nextepisode, basepattern = '\[Lilith-Raws\] 轉生成蜘蛛又怎樣！\\/ Kumo Desu ga, Nanika - \d+ \[Baha\]\[WEB-DL\]\[1080p\]\[AVC AAC\]\[CHT\]\[MP4\]')#海贼王 905 923
    print(finalbasepattern)
    for i in range(5):
        print ('')

    nextepisode,finalbasepattern,torrents = test.run("五等分的新娘",1, basepattern = '')#海贼王 905 923
    print(finalbasepattern)
    for i in range(5):
        print ('')

    nextepisode,finalbasepattern,torrents = test.run("海贼王",923, basepattern = '')#海贼王 905 923
    print(finalbasepattern)
    for i in range(5):
        print ('')
    while(len(torrents)!= 0):
        nextepisode,finalbasepattern,torrents = test.run("海贼王",nextepisode, basepattern = finalbasepattern)#海贼王 905 923
        print(finalbasepattern)
        for i in range(5):
            print ('')

