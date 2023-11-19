import socket
import threading
import os
import sys
from collections import defaultdict


class Server(object):
    def __init__(self):
        self.HOST = '172.31.98.75'
        self.PORT = 5001
        # element: {(host,port), set[title]}
        self.peers = defaultdict(list)
        # element: {title, set[(host, port)]}
        self.file_record= defaultdict(list)

    # start listenning
    def start(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.HOST, self.PORT))
        self.s.listen(5)
        print('Server is listening on port %s' % (self.PORT))
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
        # keep recieve request from client
        host = None
        port = None
        while True:
                rep = soc.recv(1024).decode()
                print('Recieve request:\n%s' % rep)
                method = rep.split()[0]
                if method == 'port': 
                    port = rep.split()[1]
                if method == 'publish':
                    host = addr[0]
                    title = rep.split()[1]
                    self.addRecord(host, port, title)
                elif method == 'fetch':
                    title = rep.split()[1]
                    self.getPeersOfRfc(soc, title)
                elif method == 'disconnect':
                    host = addr[0]
                    self.clear(host,port)
                    soc.close()
                    break



    def clear(self, host, port):
        for name in self.peers[(host, port)]:
            self.file_record[name].remove((host, port))
            if len(self.file_record[name])==0:
                self.file_record.pop(name)
        self.peers.pop((host, port))

    def addRecord(self, host, port, title):
        self.peers[(host,port)].append(title)
        self.file_record[title].append((host,port))

    def getPeersOfRfc(self, soc, title):
        if title not in self.file_record:
            msg="File name doesn't exist"
            soc.sendall(msg.encode())
        peers = ''
        for peer in self.file_record[title]:
            peers += '%s %s\n' % (peer[0], peer[1])
        soc.sendall(peers.encode())


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
        print("")
    def ping(self,hostname):
        print("")
        
if __name__ == '__main__':
    s = Server()
    s.start()
