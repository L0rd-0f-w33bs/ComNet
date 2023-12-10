import socket
import threading
import os
import sys
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
        self.PORT = 5001
        # element: {hostname,(socket,port)}
        self.online_peers = defaultdict()
        # element: {hostname,(host,list(file))}
        self.peers = defaultdict()
        # element: {title, set[host]}
        self.file_record= defaultdict(list)

    # start listenning
    def start(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.HOST, self.PORT))
        self.s.listen(5)
        print('Server is listening on %s:%s' % (self.HOST,self.PORT))
        command=threading.Thread(target=self.cmd)
        command.start()
        while True:
            soc, addr = self.s.accept()
            print('%s:%s connected' % (addr[0], addr[1]))
            thread = threading.Thread(
                target=self.handler, args=(soc, addr))
            thread.start()

    def cmd(self):
        while True:
            req = input('\ndiscover hostname: list of local files of the host named hostname,\nping hostname: live check the host named hostname,\nshutdown: Shut Down\nEnter your request: ')
            inp=req.split()
            if inp[0]=='discover' and len(inp)==2:
                self.discover(inp[1])
            elif inp[0]=='ping'and len(inp)==2:
                self.ping(inp[1])
            elif inp[0]=='shutdown'and len(inp)==1:
                self.shutdown()
            else:
                print("The system cannot recognise the command, please try again!")

    # connect with a client
    def handler(self, soc, addr):
        port = None
        hostname= None
        while True:
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
                elif method == 'fetch':
                    title = rep.split()[1]
                    self.getPeersOfRfc(soc, title)
                elif method == 'disconnect':
                    self.online_peers.pop(hostname)
                    soc.close()
                    break

    def addRecord(self, hostname, title):
        self.peers[hostname][1].append(title)
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
            return hostname + "has not connected to server yet."
        msg="discover"
        file_list=[]
        try:
            soc=self.online_peers[hostname][0]
            soc.sendall(msg.encode('utf-8'))
            rep=soc.recv(1024).decode('utf-8').splitlines()[0]
            while rep!= 'rdiscover':
                rep=soc.recv(1024).decode('utf-8').splitlines()[0]
            for file in range(1,len(rep.splitlines())):
                file_list.append(file)
            return file_list
        except:
            self.online_peers.pop(hostname)
            return hostname + " has not connected to server yet."
            
        
    def ping(self, hostname):
        if hostname not in self.online_peers:
            return hostname + " has not connected to server yet."
        msg="ping"
        try:
            soc=self.online_peers[hostname][0]
            soc.sendall(msg.encode('utf-8'))
            rep=soc.recv(1024).decode('utf-8')
            while rep!= 'rping':
                rep=soc.recv(1024).decode('utf-8')
            return "ONLINE"
        except:
            self.online_peers.pop(hostname)
            return hostname + " has not connected to server yet."
        
if __name__ == '__main__':
    s = Server()
    s.start()