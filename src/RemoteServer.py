# -*- coding: utf-8 -*-
import subprocess
import os
import time

DEBUG = 0

class RemoteDownloadServer():
    def __init__(self, hostpath = ''):
        self.server = "localhost:9091"
        self.hostpath  = hostpath
    
    def download(self, table, animatetitle, torrent):
        while self.remove_finish_torrent() > 50:
            time.sleep(300)
        title = str(animatetitle).replace(" ","_")
        if self.creat_folder(self.hostpath, table, title):
            location = self.hostpath + table +'/'+ title + '/'
            self.download_torrent(torrent, location)

    def download_torrent(self, torrent, location):
        transmission_add_torrent = ["/usr/bin/transmission-remote",self.server, "-n", "transmission:transmission",]
        transmission_add_torrent.append("-w")
        transmission_add_torrent.append(location)
        transmission_add_torrent.append("--add")
        transmission_add_torrent.append(torrent)
        subprocess.call(transmission_add_torrent)
        time.sleep(2)

    def creat_folder(self, dir, folder1, folder2):
        if not os.path.isdir(dir):
            return False
        path = dir + folder1 + '/'
        if not os.path.exists(path):
            subprocess.call(['mkdir','-m', '777',path])
        path = path + folder2 + '/'
        if not os.path.exists(path):
            subprocess.call(['mkdir','-m', '777',path]) 
        #subprocess.call(['sudo','chmod', '-R', '777', path])      
        return True        

    def List_Torrent(self)->list():
        try:
            cmd = "/usr/bin/transmission-remote " + self.server + " -n transmission:transmission -l"
            transmission_list = [cmd]
            temp, err = subprocess.Popen(transmission_list, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True).communicate()
            var = []
            temp = str(temp)
            #print (temp)
            for line in temp.split('\\n'):
                print (line)
                var.append(line)
            var.pop(-1)
            var.pop(-1)
            var.pop(0)
        except: 
            print("can not get list table")
            var = []
        return var
        
    def Romove_Torrent(self,id):
        transmission_remove = ['/usr/bin/transmission-remote',self.server, "-n", "transmission:transmission",]
        temp = str(id)
        transmission_remove.append(temp)
        temp = '-r'
        transmission_remove.append(temp)
        subprocess.call(transmission_remove)  

    def remove_finish_torrent(self): 
        check_list =  self.List_Torrent()
        count = len(check_list)
        if count == 0:
            return count
        else:
            ID ='-t'
            for item in check_list:
                temp = item.split()
                if temp[4] == 'Done':
                    ID = ID+temp[0]+','
                    count = count - 1
                else:
                    pass
            if ID != '-t':
                self.Romove_Torrent(ID)

            return count
