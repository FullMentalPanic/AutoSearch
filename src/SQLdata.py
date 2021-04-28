import pymysql
import settings
import pandas as pd
from sqlalchemy import create_engine
from SearchKeyWord import dmhy_search
import datetime
from datetime import datetime
import time
import threading
import queue
import os
import CommonFlag

class SQLClient(threading.Thread):

    def __init__(self, threadID, name, q=queue.Queue(200), hostpath = ''):
        db_connection_str = 'mysql+pymysql://'+ settings.MYSQL_USER +':'+ settings.MYSQL_PASSWD+'@'+settings.MYSQL_HOST+'/'+settings.MYSQL_DBNAME
        self.db = create_engine(db_connection_str)
        self.connection = self.db.connect()
        self.dmhy = dmhy_search()

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q  
        self.hostpath = hostpath

    def run(self):
        print("start SQLClient thread")
        #search_table = ['weekly']
        temp_date = datetime(2020, 12, 1, 0, 0)
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
            for index, row in df.iterrows():
                result = True
                num = int(row['nums'])
                pattern =  df['last_title'][index]
                #pattern = ''
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

                    #if nextepisode == num:
                    #    titles = row['othertitle'].split(',')
                    #    for title in titles:
                    #        nextepisode, pattern ,torrents = self.dmhy.run(title, num, min_time =date, basepattern = pattern)
                    #        if nextepisode != num:
                    #            break

                    if nextepisode == num:
                        result = False
                        self.update_row_data(table[0], row['animatetitle'], str(num),pattern)
                    else:
                        for torrent in torrents:
                            print("download {}, number {}".format(row['animatetitle'], num))
                            while self.q.full():
                                time.sleep(60)
                            self.q.put((table[0],row['animatetitle'],torrent))
                            num = num + 1

                        num = nextepisode
                        self.update_row_data(table[0], row['animatetitle'], str(num),pattern)
                time.sleep(1)
        self.close_sql()
        time.sleep(1)
        CommonFlag.SearchDone = 1
        print("End SQLClient thread")

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
        return pd.read_sql(tableName,self.db)

    def udpate_table(self, tableName, df = pd.DataFrame()):
        df.to_sql(tableName, self.db, if_exists="replace")
    
    def update_row_data(self, tableName, animatetitle, nums, last_title):
        #return
        try:
            SQL = """update {} set nums = \'{}\', last_title = \'{}\' where animatetitle = \'{}\' """.format(tableName, nums, last_title, animatetitle)
            self.connection.execute(SQL)
        except:
            print("can not access SQL")
    


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
            search_table.append('s'+str(now.year) + '07',date)
            date = datetime(now.year, 6, 1, 0, 0)
            search_table.append('s'+str(now.year) + '10',date)

        return search_table

    def connectSQL(self):
        self.close_sql()
        time.sleep(5)
        db_connection_str = 'mysql+pymysql://'+ settings.MYSQL_USER +':'+ settings.MYSQL_PASSWD+'@'+settings.MYSQL_HOST+'/'+settings.MYSQL_DBNAME
        self.db = create_engine(db_connection_str)
        self.connection = self.db.connect()

    def close_sql(self):
        try:
            self.connection.close()
            self.db.dispose()
        except:
            print("try to disconnect SQL")
