import pymysql
import settings
import pandas as pd
from sqlalchemy import create_engine
from RemoteServer import RemoteDownloadServer
from SearchKeyWord import dmhy_search
import datetime

class SQLClient(object):

    def __init__(self):
        db_connection_str = 'mysql+pymysql://'+ settings.MYSQL_USER +':'+ settings.MYSQL_PASSWD+'@'+settings.MYSQL_HOST+'/'+settings.MYSQL_DBNAME
        self.db = create_engine(db_connection_str)
        IP = "192.168.1.102"
        PORT = "9091"
        self.server = RemoteDownloadServer(IP, PORT)

    def run(self):
        if self.server.remote_ip_present():
            df = self.read_table('TableList')
            df['date'] = pd.to_datetime(df['date'])
            #search_table = df.loc[df['date'] == 'Updating', ['title']]
            
            now = datetime.datetime.now()
            max_date = now - datetime.timedelta(weeks = 1)
            min_date = now - datetime.timedelta(weeks = 24)
            search_table =df[(df['date'] > min_date) & (df['date'] < max_date)]
            for table in search_table['title']:
                df = self.read_table(table)
                #df['nums'] = df['nums'].apply(lambda x: int(x))
                for index, row in df.iterrows():
                    result = True
                    nums = int(row['nums'])
                    while result:
                        dmhy = dmhy_search(row['animatetitle'],[nums])
                        to_do = dmhy.run()
                        if len(to_do) == 0:
                            result = False
                            df['nums'][index] = str(nums)
                        else:
                            print("download {}, number {}".format(row['animatetitle'], nums)) 
                            torrent = [item[-1] for item in to_do]
                            #index_num =  [item[0] for item in to_do]
                            self.server.start_download(row['animatetitle'],torrent)
                            nums = nums + 1
                self.udpate_table(table,df)

    def read_table(self,tableName):
        return pd.read_sql(tableName,self.db)

    def udpate_table(self, tableName, df = pd.DataFrame()):
        df.to_sql(tableName, self.db, if_exists="replace")



    #def close(self):
    #     self.db_connection.close()
