#from SearchKeyWord import dmhy_search
#from RemoteServer import RemoteDownloadServer
from SQLdata import SQLClient
from RemoteServer import RemoteDownloadServer

import threading
import queue


#IP = "192.168.1.102"
#PORT = "9091"
#server = RemoteDownloadServer(IP, PORT)
hostpath = "/home/liang/workspace/transmission/downloads/downloads/"
q=queue.Queue(400)
event = threading.Event()
SQLtread = SQLClient(1,"Sqltread",q, event, hostpath)
downloder = RemoteDownloadServer(2, "DownloadServer", q, event, hostpath)
SQLtread.start()
downloder.start()

SQLtread.join()
downloder.join()

#SQL.close()

#if 0:#server.remote_ip_present():
#    dmhy = dmhy_search("海贼王",[911,912,913,914,915,916,917,918,919,920,921,924,923])
#    to_do = dmhy.run() 
#    torrent = [item[-1] for item in to_do]
#    index =  [item[0] for item in to_do]
#    server.start_download("海贼王",torrent)






