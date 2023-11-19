import socket
import threading
import platform
import mimetypes
import os
import sys
import time
from pathlib import Path


class Client(object):
    def __init__(self):
        self.SERVER_HOST = '172.31.98.75'
        self.SERVER_PORT = 5001
        self.sharing = False
        self.downloading = False
        self.download_path = 'downloaded'  # file directory
        Path(self.download_path).mkdir(exist_ok=True)
        self.file_dict={}
    def start(self):
        # connect to server
        print('Connecting to the server %s:%s' %
              (self.SERVER_HOST, self.SERVER_PORT))
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.connect((self.SERVER_HOST, self.SERVER_PORT))
        except Exception:
            print('Server Not Available.')
            return
        print('Connected')
        serverlike = threading.Thread(target=self.serverlike)
        serverlike.start()
        # interactive shell
        self.cmd()

    def cmd(self):
        while True:
            req = input('\npublish lname fname: To publish a file,\nfetch fname: To download a file,\nshutdown: Shutdown\nEnter your request: ')
            inp=req.split()
            if inp[0]=='publish' and len(inp)==3:
                self.publish(inp[1],inp[2])
            elif inp[0]=='fetch'and len(inp)==2:
                self.fetch(inp[1])
            elif inp[0]=='shutdown'and len(inp)==1:
                self.shutdown()
            else:
                print("The system cannot recognise the command, please try again!")
                
    def publish(self, lname, fname):
        file = Path(lname)
        if not file.is_file():
            print("This file doesn't exist!")
            return None
        self.file_dict.setdefault(fname,file)
        msg = 'publish ' + fname
        self.server.sendall(msg.encode())
        
    def fetch(self,fname):
        msg = 'fetch ' + fname 
        self.server.sendall(msg.encode())
        rep = self.server.recv(1024).decode()
        if rep=="File name doesn't exist":
            print(rep)
            return None
        lines = rep.splitlines()
        print('Available peers:\n')
        for line_idx in range(len(lines)):
            print('%d %s: %s\n' % (line_idx+1,lines[line_idx].split()[0],lines[line_idx].split()[1]))
        idx = int(input('Choose one peer to download (input): '))
        if idx > len(lines):
            while idx > len(lines):
                idx = int(input('Invalid Input. Please choose again: '))
        self.download(lines[idx-1].split()[0],lines[idx-1].split()[1],fname)

    def serverlike(self):
        # listen upload port
        self.sharer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sharer.bind(('', 0))
        self.SHARE_PORT = self.sharer.getsockname()[1]
        self.sharer.listen(5)
        while True:
            requester, addr = self.sharer.accept()
            self.sharing=True
            handler = threading.Thread(
                target=self.handle_sharing, args=(requester, addr))
            handler.start()

    def handle_sharing(self, soc, addr):
        name = soc.recv(1024).decode()
        print('\nUploading...')
        with open(self.file_dict[name], 'r') as file:
            to_send = file.read(1024)
            while to_send:
                soc.sendall(to_send.encode())
                to_send = file.read(1024)
        print('Uploading Completed.')
    # Restore CLI
        print('\npublish lname fname: To publish a file,\nfetch fname: To download a file,\nshutdown: Shutdown\nEnter your request: ')
        soc.close()


    def download(self,host,port,fname):
        # make connnection
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect_ex return errors
        soc.connect((host, int(port)))
        # make request
        soc.sendall(fname.encode())

        # Downloading
        path = '%s/%s.txt' % (self.download_path, fname)
        print('Downloading...')
        with open(path, 'w') as file:
            content = soc.recv(1024)
            while content:
                file.write(content.decode())
                content = soc.recv(1024)
        print('Downloading Completed.')
        soc.close()
            # Restore CLI
        print('\npublish lname fname: To publish a file,\nfetch fname: To download a file,\nshutdown: Shutdown\nEnter your request: ')

    def shutdown(self):
        print('\nShutting Down...')
        msg = 'disconnect '
        self.server.sendall(msg.encode())
        if self.sharing or self.downloading:
            print('\n Files are being downloaded, please wait...')
            while self.sharing or self.downloading:
                pass
        self.sharer.close()
        self.server.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == '__main__':
    client = Client()
    client.start()
