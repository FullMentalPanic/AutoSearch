import pymysql
import settings
import pandas as pd
from sqlalchemy import create_engine
from RemoteServer import RemoteDownloadServer
from SearchKeyWord import dmhy_search
import datetime
import time

class SQLClient(object):

    def __init__(self):
        db_connection_str = 'mysql+pymysql://'+ settings.MYSQL_USER +':'+ settings.MYSQL_PASSWD+'@'+settings.MYSQL_HOST+'/'+settings.MYSQL_DBNAME
        self.db = create_engine(db_connection_str)
        self.connection = self.db.connect()
        IP = "localhost"
        PORT = "9091"
        self.server = RemoteDownloadServer(IP, PORT)

    def run(self):
        if self.server.ping():
            df = self.read_table('TableList')
            df['date'] = pd.to_datetime(df['date'])            
            now = datetime.datetime.now()
            max_date = now - datetime.timedelta(weeks = 1)
            min_date = now - datetime.timedelta(weeks = 24)
            every_date = datetime.datetime.strptime('1991-01-22', '%Y-%m-%d')
            search_table =df[((df['date'] > min_date) & (df['date'] < max_date)) | (df['date'] <every_date)]
            #search_table = df
            for index_table, row_table in search_table.iterrows():
                print(row_table['title'])
                df = self.read_table(row_table['title'])
                date = row_table['date']
                for index, row in df.iterrows():
                    result = True
                    nums = int(row['nums'])
                    pattern =  df['last_title'][index]
                    print(row['animatetitle'])
                    while result:
                        retry = 0
                        try:
                            dmhy = dmhy_search(row['animatetitle'],[nums],min_time =date, basepattern = pattern)
                            to_do = dmhy.run()
                            if len(to_do) == 0:
                                result = False
                                df['nums'][index] = str(nums)
                                df['last_title'][index] = pattern
                                self.update_row_data(row_table['title'], row['animatetitle'], str(nums),pattern)
                            else:
                                print("download {}, number {}".format(row['animatetitle'], nums)) 
                                torrent = [item[-1] for item in to_do]
                                pattern = [item[0] for item in to_do][0]
                                #print (pattern)
                                #index_num =  [item[0] for item in to_do]
                                self.server.start_download(row['animatetitle'],torrent)
                                nums = nums + 1
                        except:
                            retry = retry + 1
                            if retry > 5:
                                #save broken point
                                df['nums'][index] = str(nums)
                                df['last_title'][index] = pattern
                                self.update_row_data(row_table['title'], row['animatetitle'], str(nums),pattern)
                                break
                            else:                
                                time.sleep(10)
                    self.server.remove_finish_torrent()
                    while (len(self.server.List_Torrent()) > 20):
                        time.sleep(60)
                        self.server.remove_finish_torrent()
        else:
            print ("no connection")

    def read_table(self,tableName):
        return pd.read_sql(tableName,self.db)

    def udpate_table(self, tableName, df = pd.DataFrame()):
        df.to_sql(tableName, self.db, if_exists="replace")
    
    def update_row_data(self, tableName, animatetitle, nums, last_title):
        SQL = """update {} set nums = \'{}\', last_title = \'{}\' where animatetitle = \'{}\' """.format(tableName, nums, last_title, animatetitle)
        self.connection.execute(SQL)




    #def close(self):
    #     self.db_connection.close()
