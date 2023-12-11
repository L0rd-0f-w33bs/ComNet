import socket
import threading
import os
import sys
import shutil
import queue
from pathlib import Path

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
    
class Client:
    def __init__(self, IP, port, hostname):
        self.SERVER_HOST = IP
        self.SERVER_PORT = port
        self.hostname = hostname
        self.sharing = 0
        self.downloading = False
        self.REPOSITORY = 'repository'  # file directory
        if not os.path.exists(self.REPOSITORY):
            os.makedirs(self.REPOSITORY)
        self.file_list=[]
        self.server_file = []
        filePath = os.path.join(os.getcwd(), self.REPOSITORY)
        for file in os.listdir(filePath):
            self.file_list.append(file)
        self.SHARE_PORT=None
        self.msgqueue=queue.Queue()
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
                self.fetch(inp[1])
            elif inp[0]=='getall'and len(inp)==1:
                self.get_server_files()
            elif inp[0]=='shutdown'and len(inp)==1:
                self.shutdown()
            else:
                print("The system cannot recognise the command, please try again!")
                
    def listen(self):
        while True:
            msg=self.server.recv(1024).decode('utf-8')
            if(msg=='ping'):
                rep ="ONLINE"
                self.server.sendall(rep.encode('utf-8'))
            elif(msg=='discover'):
                rep ="All files:\n"
                for key in self.file_list:
                    rep+= (key+'\n')
                self.server.sendall(rep.encode('utf-8'))
            else:
                self.msgqueue.put(msg)
                       
    def publish(self, lname, fname):
        file = os.path.join(lname, fname)
        if not os.path.exists(file):
            return("This file doesn't exist!")
        if fname in os.listdir(os.path.join(os.getcwd(), self.REPOSITORY)):
            return('File already existing in the repository.')
        shutil.copy(file, os.path.join(os.getcwd(), self.REPOSITORY))
        self.file_list.append(fname)
        msg = 'publish ' + fname
        self.server.sendall(msg.encode('utf-8'))
        return "OK"
    
    def get_server_files(self):
        msg='getall'
        self.server.sendall(msg.encode('utf-8'))
        rep=self.msgqueue.get()
        print(rep)
        self.server_file=[]
        lines = rep.splitlines()
        for line_idx in range(1,len(lines)):
            self.server_file.append(lines[line_idx])
        msg = 'Received all files from server.'
        print(msg)
        return msg
        
    def fetch(self, fname):
        msg="fetch " + fname
        self.server.sendall(msg.encode('utf-8'))
        rep=self.msgqueue.get()
        lines = rep.splitlines()
        fname=lines[0]
        print('Available peers:\n')
        self.peerswithfiles=[]
        for line_idx in range(1,len(lines)):
            self.peerswithfiles.append((lines[line_idx].split()[0],lines[line_idx].split()[1],lines[line_idx].split()[2]))
            print('%d %s  %s : %s \n' % (line_idx,lines[line_idx].split()[0],lines[line_idx].split()[1],lines[line_idx].split()[2]))
        idx = int(input('Choose one peer to download (input): '))
        if idx > len(lines):
            while idx > len(lines):
                idx = int(input('Invalid Input. Please choose again: '))
        return self.download(lines[idx].split()[1],lines[idx].split()[2],fname)

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
        self.sharing +=1
        path = '%s/%s' % (self.REPOSITORY, name)
        with open(path, 'rb') as file:
            to_send = file.read(1024)
            while to_send:
                soc.sendall(to_send)
                to_send = file.read(1024)
        self.sharing-=1
        print('Uploading Completed.')
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
        path = '%s/%s' % (self.REPOSITORY, fname)
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
        return 'Downloading Completed.'

    def shutdown(self):
        print('\nShutting Down...')
        msg = 'disconnect '
        self.server.sendall(msg.encode('utf-8'))
        if self.sharing>0 or self.downloading:
            print('\n Files are being downloaded, please wait...')
            while self.sharing>0 or self.downloading:
                pass
        self.sharer.close()
        self.server.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == '__main__':
    SERVER_IP = input("Enter server's IP: ")
    SERVER_PORT = 5011
    hostname = input("Enter your name: ")
    client = Client(SERVER_IP, SERVER_PORT, hostname)
    client.start()
