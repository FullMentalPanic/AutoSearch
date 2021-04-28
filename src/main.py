
from SQLdata import SQLClient
from RemoteServer import RemoteDownloadServer

import threading
import queue
import CommonFlag

CommonFlag.initialize()
hostpath = "/home/liang/hdd/d1/downloads/"
q=queue.Queue(400)
SQLtread = SQLClient(1,"Sqltread",q, hostpath)
downloder = RemoteDownloadServer(2, "DownloadServer", q, hostpath)

SQLtread.start()
downloder.start()

SQLtread.join()
downloder.join()







