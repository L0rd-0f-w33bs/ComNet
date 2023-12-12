import customtkinter as ctk
from client import *
from PIL import Image
import time
from tkinter import filedialog
import os
import re
from CTkListbox import *


SIZE = 1024
REPOSITORY_PATH = 'repository/'
FORMAT = 'utf-8'

def validate_ip_address(ip_address):
    # Format of IP address
    text = r"^([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})$"

    # Check if ip_address is valid?
    if re.match(text, ip_address):
        return True
    else:
        return False

class ClientUI:
    def __init__(self):
        self.app = ctk.CTk()
        self.client = Client('', 0, '')
        self.smallFont = ctk.CTkFont('Century Gothic', 15, 'bold')
        self.mediumFont = ctk.CTkFont('Century Gothic', 25, 'bold')
        self.bigFont = ctk.CTkFont('Century Gothic', 40, 'bold')
        self.setup_app()
        self.start_login()


    def setup_app(self):
        ctk.set_appearance_mode('light')
        self.app.title('Client')
        self.app.geometry('960x540')
        self.create_object()
        #self.display_main()


    def create_object(self):

        # Login Page
        self.LoginFrame = ctk.CTkFrame(self.app, 960, 540, fg_color='#059669', corner_radius=0)
        # Objects
        self.EntryFrame = ctk.CTkFrame(self.LoginFrame, 350, 200, fg_color='#059669', corner_radius=10, border_width=3, border_color='white')
        self.AppTitleLogin = ctk.CTkLabel(self.LoginFrame, text='FILE-SHARING APPLICATION', font=self.bigFont,
                                      text_color='white', corner_radius=10)
        self.AppIcon = ctk.CTkLabel(self.LoginFrame, 70, 70, fg_color='#92f5ac', text='', corner_radius=10)
        self.ServerIPLabel = ctk.CTkLabel(self.LoginFrame, 100, 30, text='Server IP:', font=self.mediumFont, 
                                          text_color='white')
        self.ServerIPEntry = ctk.CTkEntry(self.LoginFrame, 200, 30,
                                    corner_radius=10, placeholder_text='Server IP', text_color='black')
        self.HostnameLabel = ctk.CTkLabel(self.LoginFrame, 100, 30, text='Hostname:', font=self.mediumFont,
                                          text_color='white')
        self.HostnameEntry = ctk.CTkEntry(self.LoginFrame, 200, 30,
                                    corner_radius=10, placeholder_text='Hostname', text_color='black')
        self.ConnectButton = ctk.CTkButton(self.LoginFrame, text='Connect', text_color='black', command=self.connect, fg_color='#d4f592', hover_color='#92f5ac', font=self.mediumFont)

        #############################################

        # Main Page
        self.MainFrame = ctk.CTkFrame(self.app, 960, 540, fg_color='#059669', corner_radius=0)
        # Objects
        self.Avatar = ctk.CTkLabel(self.MainFrame, 60, 60, text='')
        self.AppTitleMain = ctk.CTkLabel(self.MainFrame, text='FILE-SHARING APPLICATION', font=self.bigFont,
                                      text_color='white', corner_radius=10)
        self.PublishButton = ctk.CTkButton(self.MainFrame, text='Publish file', command=self.upload, 
                                           text_color='black', fg_color='#d4f592', hover_color='#92f5ac', font=self.mediumFont)
        self.FetchButton = ctk.CTkButton(self.MainFrame, text='Fetch file', command=self.download, 
                                         text_color='black', fg_color='#d4f592', hover_color='#92f5ac', font=self.mediumFont)
        self.ViewRepoButton = ctk.CTkButton(self.MainFrame, text='My repository', command=self.view_repo, 
                                            text_color='black', fg_color='#d4f592', hover_color='#92f5ac', font=self.mediumFont)
        
        ############################################

        # My Repository
        self.RepoFrame = ctk.CTkFrame(self.MainFrame, 550, 300, fg_color='white', corner_radius=10)
        # Objects
        self.RepoTitle = ctk.CTkLabel(self.RepoFrame, fg_color='white', text='My repository', text_color='#059669', font=self.mediumFont)
        self.RepoList = CTkListbox(self.RepoFrame, fg_color='white', corner_radius=10, border_width=3, text_color='black',
                                   hover_color='#d4f592', font=self.smallFont, select_color='#92f5ac')

        ###########################################

        # Server Files
        self.ServerFileFrame = ctk.CTkFrame(self.MainFrame, 550, 300, fg_color='white', corner_radius=10)
        self.PeerFrame = ctk.CTkFrame(self.MainFrame, 550, 300, fg_color='white', corner_radius=10)
        # Objects
        self.ServerFileTitle = ctk.CTkLabel(self.ServerFileFrame, fg_color='white', text='List of files', 
                                            text_color='#059669', font=self.mediumFont)
        self.ServerFileList = CTkListbox(self.ServerFileFrame, fg_color='white', corner_radius=10, border_width=3, text_color='black',
                                   hover_color='#d4f592', font=self.smallFont, select_color='#92f5ac')
        self.PeersListTitle = ctk.CTkLabel(self.PeerFrame, fg_color='white', text='List of peers', 
                                            text_color='#059669', font=self.mediumFont)
        self.PeersList = CTkListbox(self.PeerFrame, fg_color='white', corner_radius=10, border_width=3, text_color='black',
                                   hover_color='#d4f592', font=self.smallFont, select_color='#92f5ac')
        
        # Download button
        self.DownFileButton1 = ctk.CTkButton(self.ServerFileFrame, text='Fetch', command=self.fetch_file, 
                                            fg_color='#d4f592', hover_color='#92f5ac', text_color='black', font=self.mediumFont)
        self.DownFileButton2 = ctk.CTkButton(self.PeerFrame, text='Fetch', command=self.choose_peer, 
                                            fg_color='#d4f592', hover_color='#92f5ac', text_color='black', font=self.mediumFont)
        
        # Disconnect button
        self.DisconnectButton = ctk.CTkButton(self.MainFrame, text='Disconnect', command=self.disconnect, 
                                            fg_color='white', hover_color='#92f5ac', text_color='black', font=self.mediumFont)
        

    # UI

    def start_login(self):
        self.MainFrame.place_forget()
        self.LoginFrame.place(relwidth=0.95, relheight=0.95, relx=0.5, rely=0.5, anchor=ctk.CENTER)
        self.EntryFrame.place(relwidth=0.6, relheight=0.5, relx=0.5, rely=0.7, anchor=ctk.CENTER)
        self.AppTitleLogin.place(relwidth=0.8, relheight=0.2, relx=0.5, rely=0.13, anchor=ctk.CENTER)
        self.AppIcon.configure(image=ctk.CTkImage(Image.open('logo.png'), size=(70,70)))
        self.AppIcon.place(relwidth=0.15, relheight=0.2, relx=0.5, rely=0.3, anchor=ctk.CENTER)
        self.ServerIPLabel.place(relwidth=0.2, relheight=0.08, relx=0.32, rely=0.55, anchor=ctk.CENTER)
        self.ServerIPEntry.configure(state='normal')
        self.ServerIPEntry.place(relwidth=0.3, relheight=0.08, relx=0.6, rely=0.55, anchor=ctk.CENTER)
        self.HostnameLabel.place(relwidth=0.2, relheight=0.08, relx=0.32, rely=0.68, anchor=ctk.CENTER)
        self.HostnameEntry.configure(state='normal')
        self.HostnameEntry.place(relwidth=0.3, relheight=0.08, relx=0.6, rely=0.68, anchor=ctk.CENTER)
        self.ConnectButton.place(relwidth=0.16, relheight=0.08, relx=0.5, rely=0.85, anchor=ctk.CENTER)

    
    def display_main(self):
        # Frames and Title
        self.MainFrame.place(relwidth=0.95, relheight=0.95, relx=0.5, rely=0.5, anchor=ctk.CENTER)
        self.AppTitleMain.place(relwidth=0.72, relheight=0.15, relx=0.6, rely=0.08, anchor=ctk.CENTER)
        self.RepoFrame.place(relwidth=0.7, relheight=0.76, relx=0.63, rely=0.58, anchor=ctk.CENTER)

        # Client Info
        self.Avatar.configure(image=ctk.CTkImage(Image.open('avatar.png'), size=(50,50)))
        self.Avatar.place(relx=0.05, rely=0.15, anchor=ctk.CENTER)
        self.HostnameDis = ctk.CTkLabel(self.MainFrame, 80, 15, fg_color='#059669', 
                                        text='Hostname: ' + self.client.hostname, text_color='white', font=self.smallFont)
        self.IPDis = ctk.CTkLabel(self.MainFrame, 80, 15, fg_color='#059669', text='Your IP: ' + get_local_ip(),
                                  text_color='white', font=self.smallFont)
        self.ServerIPDis = ctk.CTkLabel(self.MainFrame, 80, 15, fg_color='#059669', text='Server IP: ' + self.client.SERVER_HOST,
                                  text_color='white', font=self.smallFont)
        self.HostnameDis.place(relx=0.18, rely=0.13, anchor=ctk.CENTER)
        self.IPDis.place(relx=0.18, rely=0.17, anchor=ctk.CENTER)
        self.ServerIPDis.place(relx=0.12, rely=0.9, anchor=ctk.CENTER)

        # Buttons
        self.PublishButton.place(relwidth=0.2, relheight=0.08, relx=0.12, rely=0.3, anchor=ctk.CENTER)
        self.FetchButton.place(relwidth=0.2, relheight=0.08, relx=0.12, rely=0.45, anchor=ctk.CENTER)
        self.ViewRepoButton.place(relwidth=0.2, relheight=0.08, relx=0.12, rely=0.6, anchor=ctk.CENTER)
        self.DisconnectButton.place(relwidth=0.2, relheight=0.08, relx=0.12, rely=0.8, anchor=ctk.CENTER)

        self.view_repo()


    # Functions for buttons

    def connect(self):
        SERVER_IP = self.ServerIPEntry.get()
        SERVER_PORT = 5011
        hostname = self.HostnameEntry.get()
        if not SERVER_IP or not hostname:
            # Handle empty fields
            self.WarningLabel = ctk.CTkLabel(self.LoginFrame, text='Please enter both Server IP and Hostname!',
                                              text_color='white', font=self.smallFont)
            self.WarningLabel.place(relx=0.5, rely=0.76, anchor=ctk.CENTER)
            self.WarningLabel.after(2000, lambda: self.WarningLabel.place_forget())
            return
        
        if not validate_ip_address(SERVER_IP):
            # Handle invalid IP address
            self.WarningLabel = ctk.CTkLabel(self.LoginFrame, text='Server IP is not valid!',
                                              text_color='white', font=self.smallFont)
            self.WarningLabel.place(relx=0.5, rely=0.76, anchor=ctk.CENTER)
            self.WarningLabel.after(2000, lambda: self.WarningLabel.place_forget())
            return

        self.client = Client(SERVER_IP, SERVER_PORT, hostname)
        self.client.start()
        time.sleep(0.5)
        # Hide the LoginFrame
        self.LoginFrame.pack_forget()
        # Display the MainFrame
        self.display_main()
        

    def upload(self):
        filePath = filedialog.askopenfilename()
        lname, fname = os.path.split(filePath)
        msg = self.client.publish(lname, fname)
        MessageLabel = ctk.CTkLabel(self.MainFrame, text=msg, text_color='white', font=self.smallFont)
        MessageLabel.place(relx=0.12, rely=0.7, anchor=ctk.CENTER)
        MessageLabel.after(2000, lambda:MessageLabel.place_forget())
        
        # Update Repository after uploading
        self.update_RepoList()
        self.view_repo()


    def download(self):
        self.view_server()
        self.DownFileButton1.place(relwidth=0.25, relheight=0.08, relx=0.5, rely=0.87, anchor=ctk.CENTER)


    def chooseIP(self):
        self.view_peer()
        self.DownFileButton2.place(relwidth=0.25, relheight=0.08, relx=0.5, rely=0.87, anchor=ctk.CENTER)

    def view_repo(self):
        self.ServerFileFrame.place_forget()
        self.PeerFrame.place_forget()
        self.update_RepoList()
        self.RepoFrame.place(relwidth=0.73, relheight=0.76, relx=0.61, rely=0.58, anchor=ctk.CENTER)
        self.RepoTitle.place(relwidth=0.9, relheight=0.2, relx=0.5, rely=0.1, anchor=ctk.CENTER)
        self.RepoList.place(relwidth=0.9, relheight=0.6, relx=0.5, rely=0.5, anchor=ctk.CENTER)


    def view_server(self):
        self.RepoFrame.place_forget()
        self.DownFileButton1.place_forget()
        self.DownFileButton2.place_forget()
        self.PeerFrame.place_forget()
        self.update_ServerFileList()
        self.ServerFileFrame.place(relwidth=0.73, relheight=0.76, relx=0.61, rely=0.58, anchor=ctk.CENTER)
        self.ServerFileTitle.place(relwidth=0.9, relheight=0.2, relx=0.5, rely=0.1, anchor=ctk.CENTER)
        self.ServerFileList.place(relwidth=0.9, relheight=0.6, relx=0.5, rely=0.5, anchor=ctk.CENTER)


    def view_peer(self):
        self.RepoFrame.place_forget()
        self.DownFileButton1.place_forget()
        self.DownFileButton2.place_forget()
        self.ServerFileFrame.place_forget()
        self.getPeers()
        self.PeerFrame.place(relwidth=0.73, relheight=0.76, relx=0.61, rely=0.58, anchor=ctk.CENTER)
        self.PeersListTitle.place(relwidth=0.9, relheight=0.2, relx=0.5, rely=0.1, anchor=ctk.CENTER)
        self.PeersList.place(relwidth=0.9, relheight=0.6, relx=0.5, rely=0.5, anchor=ctk.CENTER)


    def fetch_file(self):
        fName = self.ServerFileList.get()
        if fName == None:
            msg = 'Please select a file to fetch!'
            MessageLabel = ctk.CTkLabel(self.ServerFileFrame, text=msg, text_color='#059669', font=self.smallFont)
            MessageLabel.place(relx=0.5, rely=0.95, anchor=ctk.CENTER)
            MessageLabel.after(2000, lambda:MessageLabel.place_forget())
        else:
            msg = self.client.fetch(self.ServerFileList.get())
            time.sleep(0.5)
            self.chooseIP()

    def choose_peer(self):
        hostname,host,port = self.PeersList.get()
        fname=self.client.fname
        msg=self.client.choose_peer(host,port,fname)
        self.RepoList.insert('END', self.ServerFileList.get())
        MessageLabel = ctk.CTkLabel(self.MainFrame, text=msg, text_color='white', font=self.smallFont)
        MessageLabel.place(relx=0.12, rely=0.7, anchor=ctk.CENTER)
        MessageLabel.after(2000, lambda:MessageLabel.place_forget())
        self.update_ServerFileList()
        self.view_repo()


    def disconnect(self):
        self.update_RepoList()
        self.update_ServerFileList()
        self.client.shutdown()
        self.app.destroy()

    # Others functions

    def update_RepoList(self):
        if self.RepoList.size():
            self.RepoList.delete(0,'END')
        filePath = os.path.join(os.getcwd(), REPOSITORY_PATH)
        for fileName in os.listdir(filePath):
            self.RepoList.insert('END',fileName)


    def getPeers(self):
        if self.PeersList.size():
            self.PeersList.delete(0,'END')
        for peer in self.client.peerswithfile:
            self.PeersList.insert('END',peer)


    def update_ServerFileList(self):
        self.client.get_server_files()
        if self.ServerFileList.size():
            self.ServerFileList.delete(0,'END')
        for fileName in self.client.server_file:
            self.ServerFileList.insert('END',fileName)


if __name__ == '__main__':
    UI = ClientUI()
    UI.app.mainloop()
