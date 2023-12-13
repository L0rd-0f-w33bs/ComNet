import socket
import threading
import os
import sys
import queue
from collections import defaultdict

def get_local_ip():
    try:
        # Create a socket to get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(('8.8.8.8', 80))  
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except socket.error:
        return None
    
class Server:
    def __init__(self):
        self.HOST = get_local_ip()
        self.PORT = 5011
        # element: {hostname,(socket,port)}
        self.online_peers = defaultdict()
        # element: {hostname,(host,list(file))}
        self.peers = defaultdict()
        # element: {title, list[host]}
        self.file_record= defaultdict(list)
        self.msgqueue=queue.Queue()
    # start listenning
    
    def start(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.HOST, self.PORT))
        self.s.listen(5)
        print('Server is listening on %s:%s' % (self.HOST,self.PORT))
        while True:
            soc, addr = self.s.accept()
            print('%s:%s connected' % (addr[0], addr[1]))
            thread = threading.Thread(
                target=self.handler, args=(soc, addr))
            thread.start()

    # connect with a client
    def handler(self, soc, addr):
        port = None
        hostname= None
        while True:
                try:
                    rep = soc.recv(1024).decode('utf-8')
                    print('Recieve request:\n%s' % rep)
                    method = rep.split()[0]
                    if method == 'info': 
                        port = rep.split()[1]
                        hostname=rep.split()[2]
                        self.online_peers[hostname]=(soc,port)
                        self.peers[hostname]=(addr[0],[])
                    elif method == 'publish':
                        title = rep.split()[1]
                        self.addRecord(hostname,title)
                    elif method == 'getall':
                        self.getAll(soc)
                    elif method == 'fetch':
                        title = rep.split()[1]
                        self.getPeersOfRfc(soc, title)
                    elif method == 'disconnect':
                        self.online_peers.pop(hostname)
                        soc.close()
                        break
                    else:
                        self.msgqueue.put(rep)
                
                except TimeoutError as e:
                    self.online_peers.pop(hostname)
                    soc.close()
                    print (hostname + " has not connected to server yet.")
                    self.msgqueue.put("OFFLINE")
                finally:
                    if hostname not in self.online_peers:
                        soc.close()
                        break


    def addRecord(self, hostname, title):
        self.peers[hostname][1].append(title)
        print(self.peers[hostname][1])
        self.file_record[title].append(hostname)
        
    def getPeersOfRfc(self, soc, title):
        if title not in self.file_record:
            msg="File name doesn't exist"
            soc.sendall(msg.encode('utf-8'))
            return
        peers = title+'\n'
        for peer in self.file_record[title]:
            if peer in self.online_peers:
                peers += '%s %s %s\n' % (peer,self.peers[peer][0], self.online_peers[peer][1])
        soc.sendall(peers.encode('utf-8'))
        
    def getAll(self, soc):
        filelist = 'All files:\n'
        for title in self.file_record:
            filelist += '%s\n' % title
        soc.sendall(filelist.encode('utf-8'))

    def shutdown(self):
        print('\nShutting Down...')
        if not self.peers:
            print('\n There are peers still connected, please wait...')
            while not self.peers:
                pass
        self.s.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    def discover(self, hostname):
        if hostname not in self.online_peers:
            print (hostname + " has not connected to server yet.")
            return "OFFLINE"
        msg="discover"
        file_list=[]
        try:
            soc=self.online_peers[hostname][0]
            soc.sendall(msg.encode('utf-8'))
            rep=self.msgqueue.get()
            file=rep.splitlines()
            for idx in range(1,len(file)):
                file_list.append(file[idx])
                print(file[idx])
                if file[idx] not in self.file_record:
                    self.file_record[file[idx]].append(hostname)
                else:
                    if hostname not in self.file_record[file[idx]]:
                        self.file_record[file[idx]].append(hostname)
            return file_list
        except:
            self.online_peers[hostname][0].close()
            self.online_peers.pop(hostname)
            print (hostname + " has not connected to server yet.")
            return "OFFLINE"
        
    def ping(self, hostname):
        if hostname not in self.online_peers:
            print (hostname + " has not connected to server yet.")
            return "OFFLINE"
        msg="ping"
        try:
            soc=self.online_peers[hostname][0]
            soc.sendall(msg.encode('utf-8'))
            msg=self.msgqueue.get()
            print (hostname + " is "+ msg)
            return msg
        except:
            self.online_peers[hostname][0].close()
            self.online_peers.pop(hostname)
            print (hostname + " has not connected to server yet.")
            return "OFFLINE"
    
    def stop(self):
        self.s.close()
        sys.exit(0)
