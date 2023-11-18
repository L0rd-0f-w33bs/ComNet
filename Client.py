import socket
import threading
import platform
import mimetypes
import os
import sys
import time
from pathlib import Path
class MyException(Exception):
    pass


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
            req = input('\npublish lname fname: To publish a file,\nfetch fname: To download a file,\nshut down: Shut Down\nEnter your request: ')
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
            raise MyException("This file doesn't exist!")
        self.file_dict.update[fname]=file
        msg = 'publish ' + fname
        self.server.sendall(msg.encode())
        res = self.server.recv(1024).decode()
        print('Recieve response: \n%s' % res)
        
    def fetch(self,fname):
        msg = 'fetch \n'
        msg += fname 
        self.server.sendall(msg.encode())
        rep = self.server.recv(1024).decode()
        host = rep.split()[0]
        port = int(rep.split()[1])
        name  = rep.split()[2]
        self.download(self,host,port,name)

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
        mes = soc.recv(1024).decode().splitlines()
        try:
            name = mes[0].split()[0]
            print('\nUploading...')
            send_length = 0
            with open(self.file_dict[name], 'r') as file:
                to_send = file.read(1024)
                while to_send:
                    send_length += len(to_send.encode())
                    soc.sendall(to_send.encode())
                    to_send = file.read(1024)
        except Exception:
            raise MyException('Uploading Failed')
        # total_length = int(os.path.getsize(path))
        # print('send: %s | total: %s' % (send_length, total_length))
        # if send_length < total_length:
        #     raise MyException('Uploading Failed')
        else:
            print('Uploading Completed.')
        # Restore CLI
            print('\n1: Add, 2: Look Up, 3: List All, 4: Download\nEnter your request: ')
        finally:
            soc.close()


    def lookup(self):
        num = input('Enter the RFC number: ')
        title = input('Enter the RFC title(optional): ')
        msg = 'LOOKUP RFC %s %s\n' % (num, self.V)
        msg += 'Host: %s\n' % socket.gethostname()
        msg += 'Post: %s\n' % self.UPLOAD_PORT
        msg += 'Title: %s\n' % title
        self.server.sendall(msg.encode())
        res = self.server.recv(1024).decode()
        print('Recieve response: \n%s' % res)

    def listall(self):
        l1 = 'LIST ALL %s\n' % self.V
        l2 = 'Host: %s\n' % socket.gethostname()
        l3 = 'Post: %s\n' % self.UPLOAD_PORT
        msg = l1 + l2 + l3
        self.server.sendall(msg.encode())
        res = self.server.recv(1024).decode()
        print('Recieve response: \n%s' % res)

    def pre_download(self):
        num = input('Enter the RFC number: ')
        msg = 'LOOKUP RFC %s %s\n' % (num, self.V)
        msg += 'Host: %s\n' % socket.gethostname()
        msg += 'Post: %s\n' % self.UPLOAD_PORT
        msg += 'Title: Unkown\n'
        self.server.sendall(msg.encode())
        lines = self.server.recv(1024).decode().splitlines()
        if lines[0].split()[1] == '200':
            # Choose a peer
            print('Available peers: ')
            for i, line in enumerate(lines[1:]):
                line = line.split()
                print('%s: %s:%s' % (i + 1, line[-2], line[-1]))

            try:
                idx = int(input('Choose one peer to download: '))
                title = lines[idx].rsplit(None, 2)[0].split(None, 2)[-1]
                peer_host = lines[idx].split()[-2]
                peer_port = int(lines[idx].split()[-1])
            except Exception:
                raise MyException('Invalid Input.')
            # exclude self
            if((peer_host, peer_port) == (socket.gethostname(), self.UPLOAD_PORT)):
                raise MyException('Do not choose yourself.')
            # send get request
            
        elif lines[0].split()[1] == '400':
            raise MyException('Invalid Input.')
        elif lines[0].split()[1] == '404':
            raise MyException('File Not Available.')
        elif lines[0].split()[1] == '500':
            raise MyException('Version Not Supported.')

    def download(self,host,port,name):
        try:
            # make connnection
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connect_ex return errors
            if soc.connect_ex((host, port)):
                # print('Try Local Network...')
                # if soc.connect_ex(('localhost', peer_port)):
                raise MyException('Peer Not Available')
            # make request
            msg = 'GET RFC %s %s\n' % (num, self.V)
            msg += 'Host: %s\n' % socket.gethostname()
            msg += 'OS: %s\n' % platform.platform()
            soc.sendall(msg.encode())

            # Downloading

            header = soc.recv(1024).decode()
            print('Recieve response header: \n%s' % header)
            header = header.splitlines()
            if header[0].split()[-2] == '200':
                path = '%s/rfc%s.txt' % (self.DIR, num)
                print('Downloading...')
                try:
                    with open(path, 'w') as file:
                        content = soc.recv(1024)
                        while content:
                            file.write(content.decode())
                            content = soc.recv(1024)
                except Exception:
                    raise MyException('Downloading Failed')

                total_length = int(header[4].split()[1])
                # print('write: %s | total: %s' % (os.path.getsize(path), total_length))

                if os.path.getsize(path) < total_length:
                    raise MyException('Downloading Failed')

                print('Downloading Completed.')
                # Share file, send ADD request
                print('Sending ADD request to share...')
            elif header[0].split()[1] == '400':
                raise MyException('Invalid Input.')
            elif header[0].split()[1] == '404':
                raise MyException('File Not Available.')
            elif header[0].split()[1] == '500':
                raise MyException('Version Not Supported.')
        finally:
            soc.close()
            # Restore CLI
          #  print('\n1: Add, 2: Look Up, 3: List All, 4: Download\nEnter your request: ')

    def invalid_input(self):
        raise MyException('Invalid Input.')

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
