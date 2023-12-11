import socket
import threading
import os
import sys
from pathlib import Path


class Client:
    def __init__(self, IP, port, hostname):
        self.SERVER_HOST = IP
        self.SERVER_PORT = port
        self.hostname = hostname
        self.sharing = False
        self.downloading = False
        self.download_path = 'downloaded'  # file directory
        Path(self.download_path).mkdir(exist_ok=True)
        self.file_dict={}
        self.SHARE_PORT=None
    def start(self):
        # connect to server
        print('Connecting to the server %s:%s' %
              (self.SERVER_HOST, self.SERVER_PORT))
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.connect((self.SERVER_HOST, self.SERVER_PORT))
        except Exception:
            print('Server Not Available!')
            return
        print('Connected!')
        serverlike = threading.Thread(target=self.serverlike)
        serverlike.start()
        while self.SHARE_PORT==None:
            pass
        msg="info "+ str(self.SHARE_PORT) + " "+ self.hostname
        self.server.sendall(msg.encode('utf-8'))
        listentoserver = threading.Thread(target=self.listen)
        listentoserver.start()
        # interactive shell
        self.cmd()

    def cmd(self):
        while True:
            req = input('\n> publish lname fname: To publish a file,\n> fetch fname: To download a file,\nshutdown: Shutdown\nEnter your request: ')
            inp=req.split()
            if inp[0]=='publish' and len(inp)==3:
                self.publish(inp[1],inp[2])
            elif inp[0]=='fetch'and len(inp)==2:
                msg = 'fetch ' + inp[1]
                self.server.sendall(msg.encode('utf-8'))
            elif inp[0]=='shutdown'and len(inp)==1:
                self.shutdown()
            else:
                print("The system cannot recognise the command, please try again!")
    def listen(self):
        while True:
            msg=self.server.recv(1024).decode('utf-8')
            if(msg=='ping'):
                rep ="rping"
                self.server.sendall(rep.encode('utf-8'))
            elif(msg=='discover'):
                rep ="rdiscover\n"
                for key in self.file_dict:
                    rep+= (key+'\n')
                self.server.sendall(rep.encode('utf-8'))
            else:
                self.choose_client(msg)
                
                    
    def publish(self, lname, fname):
        file = Path(lname)
        if not file.is_file():
            print("This file doesn't exist!")
            return None
        self.file_dict[fname]=file
        msg = 'publish ' + fname
        self.server.sendall(msg.encode('utf-8'))
        
        
    def choose_client(self, rep):
        if rep=="File name doesn't exist!":
            print(rep)
            return 
        lines = rep.splitlines()
        fname=lines[0]
        print('Available peers:\n')
        for line_idx in range(1,len(lines)):
            print('%d %s  %s : %s \n' % (line_idx,lines[line_idx].split()[0],lines[line_idx].split()[1],lines[line_idx].split()[2]))
        idx = int(input('Choose one peer to download (input): '))
        if idx > len(lines):
            while idx > len(lines):
                idx = int(input('Invalid Input. Please choose again: '))
        self.download(lines[idx].split()[1],lines[idx].split()[2],fname)

    def serverlike(self):
        # listen upload port
        self.sharer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sharer.bind(('', 0))
        self.SHARE_PORT = self.sharer.getsockname()[1]
        self.sharer.listen(5)
        while True:
            requester,addr= self.sharer.accept()
            self.sharing=True
            handler = threading.Thread(
                target=self.handle_sharing, args=(requester,))
            handler.start()

    def handle_sharing(self, soc):
        name = soc.recv(1024).decode('utf-8')
        print('\nUploading...')
        self.sharing=True
        with open(self.file_dict[name], 'rb') as file:
            to_send = file.read(1024)
            while to_send:
                soc.sendall(to_send)
                to_send = file.read(1024)
        self.sharing=False
        print('Uploading Completed!')
    # Restore CLI
        print('\n> publish lname fname: To publish a file,\n> fetch fname: To download a file,\nshutdown: Shutdown\nEnter your request: ')
        soc.close()


    def download(self,host,port,fname):
        # make connnection
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect_ex return errors
        soc.connect((host, int(port)))
        # make request
        soc.sendall(fname.encode('utf-8'))

        # Downloading
        self.downloading=True
        path = '%s/%s' % (self.download_path, fname)
        print('Downloading...')
        with open(path, 'wb') as file:
            content = soc.recv(1024)
            while content:
                file.write(content)
                content = soc.recv(1024)
        print('Downloading Completed!')
        self.downloading=True
        soc.close()
            # Restore CLI
        print('\n> publish lname fname: To publish a file,\n> fetch fname: To download a file,\nshutdown: Shutdown\nEnter your request: ')

    def shutdown(self):
        print('\nShutting Down...')
        msg = 'disconnect '
        self.server.sendall(msg.encode('utf-8'))
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
    SERVER_IP = input("Enter server's IP: ")
    SERVER_PORT = 5001
    hostname = input("Enter your name: ")
    client = Client(SERVER_IP, SERVER_PORT, hostname)
    client.start()
