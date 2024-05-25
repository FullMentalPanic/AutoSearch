
import pandas as pd
from SearchKeyWord import dmhy_search
from RemoteServer import RemoteDownloadServer
import datetime
from datetime import datetime
import os

csvBasePath='/home/liang/hdd/d1/recording/'

class DownloadByCsv(RemoteDownloadServer):

    def __init__(self, hostpath = ''):
        super(DownloadByCsv, self).__init__(hostpath = '')
        self.dmhy = dmhy_search()
        self.hostpath = hostpath

    def run(self):
        self.remove_finish_torrent()
        temp_date = datetime(2020, 12, 1, 0, 0)
        dt = datetime.now()
        weekyday = dt.weekday()
        search_table = [('weekly',temp_date)]
        search_table += self.generate_search_table()
        for table in search_table:
            print(table)
            try:
                df = self.read_table(table[0])
            except:
                print("can not find table")
                continue
            date = table[1]
            count = 0
            start = weekyday * 10
            end = (weekyday + 1) * 10
            try:
                for index, row in df.iterrows():
                    if count < start:
                        count += 1
                        continue
                    if count >= end:
                        count += 1
                        continue
                    count += 1
                    result = True
                    num = int(row['nums'])
                    pattern =  df['last_title'][index]
                    print(row['animatetitle'])
                    hd = True
                    if row['animatetitle'] == '黑色五葉草':
                        hd = False # workaround 
                    while result:
                        if row['cross_s'] == 'Y' and self.check_exist(table[0],row['animatetitle']):
                            print("already exist last season")
                            result = False
                            break

                        nextepisode, pattern ,torrents = self.dmhy.run(row['animatetitle'], num, min_time =date, basepattern = pattern,HD = hd)

                        if nextepisode == num:
                            result = False
                            df['last_title'][index] = pattern
                            df['nums'][index] = str(num)
                        else:
                            for torrent in torrents:
                                print("download {}, number {}".format(row['animatetitle'], num))
                                self.download(table[0],row['animatetitle'],torrent)
                                num = num + 1
                            num = nextepisode
                            df['last_title'][index] = pattern
                            df['nums'][index] = str(num)
            except Exception as err:
                self.update_table(table[0], df)
                raise err
            self.update_table(table[0], df)

    def check_exist(self,table,title):
        animatetitle = str(title).replace(" ","_")
        year = int(table[1:5])
        month = int(table[5:7])
        if month == 1:
            month = str(10)
            year = str(year - 1)
        else:
            month = month - 3
            month = '0' + str(month)
            year = str(year)
        tablefolder = 's' + str(year) +month
        location = self.hostpath + tablefolder +'/'+ animatetitle + '/'
        if os.path.exists(location):
            return True
        else:
            return False

    def read_table(self,tableName):
        file = csvBasePath+tableName+'.csv'
        df = pd.read_csv(file)
        df = df.fillna('')
        return df

    def update_table(self, tableName, df = pd.DataFrame()):
        file = csvBasePath+tableName+'.csv'
        df.to_csv(file,index=False)

    def generate_search_table(self):
        now = datetime.now()
        search_table = []
        if now.month < 4:
            date = datetime(now.year - 1, 6, 1, 0, 0)
            search_table.append(('s'+str(now.year - 1) + '10',date))
            date = datetime(now.year -1, 9, 1, 0, 0)
            search_table.append(('s'+str(now.year) + '01',date))

        elif now.month < 7:
            date = datetime(now.year -1, 9, 1, 0, 0)
            search_table.append(('s'+str(now.year) + '01',date))
            date = datetime(now.year-1, 12, 1, 0, 0)
            search_table.append(('s'+str(now.year) + '04',date))

        elif now.month < 10:
            date = datetime(now.year-1, 12, 1, 0, 0)
            search_table.append(('s'+str(now.year) + '04',date))
            date = datetime(now.year, 3, 1, 0, 0)
            search_table.append(('s'+str(now.year) + '07',date))

        elif now.month <= 12:
            date = datetime(now.year, 3, 1, 0, 0)
            search_table.append(('s'+str(now.year) + '07',date))
            date = datetime(now.year, 6, 1, 0, 0)
            search_table.append(('s'+str(now.year) + '10',date))

        return search_table

