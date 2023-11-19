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
        self.peers = defaultdict(set)
        # element: {title, set[(host, port)]}
        self.file_record= {}

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
            try:
                rep = soc.recv(1024).decode()
                print('Recieve request:\n%s' % rep)
                method = rep.split()[0]
                if method == 'publish':
                    host = addr[0]
                    port = addr[1]
                    title = rep.split()[1]
                    self.addRecord(soc, (host, port), title)
                elif method == 'fetch':
                    title = rep.split()[1]
                    self.getPeersOfRfc(soc, title)
                elif method == 'disconnect':
                    host = addr[0]
                    port = addr[1]
                    self.clear(host,port)
                else:
                    raise AttributeError('Method Not Match')
            except ConnectionError:
                print('%s:%s left' % (addr[0], addr[1]))
                # Clean data if necessary
                if host and port:
                    self.clear(host,port)
                soc.close()
                break


    def clear(self, host, port):
        nums = self.peers[(host, port)]
        for num in nums:
            self.rfcs[num][1].discard((host, port))
        if not self.rfcs[num][1]:
            self.rfcs.pop(num, None)
        self.peers.pop((host, port), None)

    def addRecord(self, soc, peer, num, title):
        self.peers[peer].add(num)
        self.rfcs.setdefault(num, (title, set()))[1].add(peer)
        # print(self.rfcs)
        # print(self.peers)
        header = self.V + ' 200 OK\n'
        header += 'RFC %s %s %s %s\n' % (num,
                                         self.rfcs[num][0], peer[0], peer[1])
        soc.sendall(str.encode(header))

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
