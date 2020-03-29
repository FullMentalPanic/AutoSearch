# -*- coding: utf-8 -*-
import subprocess
import os
import time
import psutil
import platform    # For getting the operating system name

DEBUG = 0

class RemoteDownloadServer(object):
    def __init__(self,ip= str(),port=str()):
        print("Transmission is start....")
        self.server = ip + ':'+port
        self.ip = ip
        self.ssh_user = "root@"+ ip
    
    def start_download(self,keyword = str(),torrents = list()):
        for torrent in torrents:
            self.download_torrent(torrent,keyword)


    def download_torrent(self, torrent, location):
        base_path = "/downloads/"
        temp = str(location).replace(" ","_")
        abs_path = (base_path + temp+'/')#encode('utf-8')
        self.creat_folder(abs_path)
        transmission_add_torrent = ["/usr/bin/transmission-remote",self.server, "-n", "transmission:transmission",]
        transmission_add_torrent.append("--add")
        transmission_add_torrent.append(torrent)
        transmission_add_torrent.append("-w")
        transmission_add_torrent.append(abs_path)
        subprocess.call(transmission_add_torrent)

    def creat_folder(self, dir):
        real_path = "/var/media/sda1-usb-External_USB3.0_"+ dir
        cmd_mkdir = ["ssh " + self.ssh_user + " \'[ -d "+real_path +" ] && echo ok  || mkdir -p "+real_path + "\'"]
        cmd_chmod = ["ssh " + self.ssh_user + " \'chmod -R 777 "+ real_path +"\'"]
        temp, err = subprocess.Popen(cmd_mkdir, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True).communicate()
        temp, err = subprocess.Popen(cmd_chmod, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True).communicate()
        #ssh user@192.168.3.131 "[ -d /var/test ] && echo ok || mkdir -p /var/test"
        #subprocess.call(["ssh",cmd_mkdir])
        #subprocess.call(["ssh",cmd_chmod])

    def remote_ips(self):
        remote_ips = []
        for process in psutil.process_iter():
            try:
                connections = process.connections(kind='inet')
            except psutil.AccessDenied or psutil.NoSuchProcess:
                pass
            else:
                for connection in connections:
                    if connection.raddr and connection.raddr[0] not in remote_ips:
                        remote_ips.append(connection.raddr[0])
        return remote_ips

    def remote_ip_present(self):
        return self.ip in self.remote_ips() 


    def ping(self):
        # Option for the number of packets as a function of
        param = '-n' if platform.system().lower()=='windows' else '-c'
        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '1', self.ip]

        return subprocess.call(command) == 0

    def List_Torrent(self):
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
        if not check_list:
            pass
        else:
            ID ='-t'
            for item in check_list:
                temp = item.split()
                if temp[4] == 'Done':
                    ID = ID+temp[0]+','
                else:
                    pass
            if ID != '-t':
                self.Romove_Torrent(ID)

if DEBUG == 1:
    IP = "192.168.1.102"
    PORT = "9091"
    server = RemoteDownloadServer(IP, PORT)
    if server.ping():
        print ("connect")
    else:
        print("No connect")