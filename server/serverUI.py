import customtkinter as ctk
from server import *
import threading
from PIL import Image
from CTkListbox import *


SERVER_IP = get_local_ip()
SERVER_PORT = 4869

SIZE = 1024
FORMAT = 'utf-8'


class ServerUI:
    def __init__(self):
        self.app = ctk.CTk()
        self.server = Server(SERVER_IP, SERVER_PORT)
        self.smallFont = ctk.CTkFont('Century Gothic', 15, 'bold')
        self.mediumFont = ctk.CTkFont('Century Gothic', 25, 'bold')
        self.bigFont = ctk.CTkFont('Century Gothic', 50, 'bold')
        #self.ClientListName = list()
        self.setup_app()
        self.display_main()

    
    def setup_app(self):
        ctk.set_appearance_mode('light')
        self.app.title('Server')
        self.app.geometry('960x540')
        threading.Thread(target=self.start_server).start()
        self.create_object()


    def create_object(self):
        self.MainFrame = ctk.CTkFrame(self.app, 960, 540, fg_color='#059669', corner_radius=10)
        self.AppTitle = ctk.CTkLabel(self.MainFrame, text='FILE-SHARING APPLICATION', font=self.bigFont,
                                      text_color='white', corner_radius=15)
        self.ServerInfo = ctk.CTkLabel(self.app, text='Server IP: ' + get_local_ip(), font=self.mediumFont,
                                       text_color='white', fg_color='#059669', bg_color='#059669')
        self.ClientListBox = CTkListbox(self.MainFrame, fg_color='#ffffff', corner_radius=10, border_width=3, text_color='black',
                                   hover_color='#d4f592', font=self.smallFont, select_color='#92f5ac')
        self.IPHeader = ctk.CTkLabel(self.MainFrame, fg_color='#333333',
                                     text='Client IP', font=self.mediumFont, text_color='white', corner_radius=10)
        self.NameHeader = ctk.CTkLabel(self.MainFrame, fg_color='#333333',
                                       text='Client Name', font=self.mediumFont, text_color='white', corner_radius=10)
        self.RepoList = CTkListbox(self.MainFrame, fg_color='#ffffff', corner_radius=10, border_width=3, text_color='black',
                                   hover_color='#d4f592', font=self.smallFont, select_color='#92f5ac')
        self.PingButton = ctk.CTkButton(self.MainFrame, fg_color='#d4f592', corner_radius=5, text_color='black',
                                        text='Ping', font=self.mediumFont, hover_color='#92f5ac', command=self.ping)
        self.DiscoverButton = ctk.CTkButton(self.MainFrame, fg_color='#d4f592', corner_radius=5, text_color='black',
                                        text='Discover', font=self.mediumFont, hover_color='#92f5ac', command=self.discover)
        self.RefreshButton = ctk.CTkButton(self.NameHeader, 20, 20, fg_color='#333333', text='',
                                            hover_color='#666666', command=self.update_client_listbox)

    def display_main(self):
        self.MainFrame.place(relwidth=0.95, relheight=0.95, relx=0.5, rely=0.5, anchor=ctk.CENTER)
        self.AppTitle.place(relwidth=0.8, relheight=0.15, relx=0.5, rely=0.08, anchor=ctk.CENTER)
        self.ServerInfo.place(relx=0.5, rely=0.2, anchor=ctk.CENTER)
        self.ClientListBox.place(relwidth=0.6, relheight=0.6, relx=0.32, rely=0.65, anchor=ctk.CENTER)
        self.IPHeader.place(relwidth=0.18, relheight=0.08, relx=0.11, rely=0.3, anchor=ctk.CENTER)
        self.NameHeader.place(relwidth=0.42, relheight=0.08, relx=0.41, rely=0.3, anchor=ctk.CENTER)
        self.RefreshButton.configure(image=ctk.CTkImage(Image.open('refresh.png'), size=(28,28)))
        self.RefreshButton.place(relwidth=0.15, relheight=0.8, relx=0.9, rely=0.5, anchor=ctk.CENTER)
        self.RepoList.place(relwidth=0.34, relheight=0.4, relx=0.81, rely=0.75, anchor=ctk.CENTER)
        self.PingButton.place(relwidth=0.16, relheight=0.08, relx=0.72, rely=0.3, anchor=ctk.CENTER)
        self.DiscoverButton.place(relwidth=0.16, relheight=0.08, relx=0.9, rely=0.3, anchor=ctk.CENTER)


    def ping(self):
        client = self.ClientListBox.get()
        if client == None:
            msg = 'Please select any client to ping!'
            MessageLabel = ctk.CTkLabel(self.MainFrame, text=msg, text_color='white', font=self.smallFont)
        else:
            hostname = client.split('\t')[-1]
            status = self.server.ping(hostname)
            MessageLabel = ctk.CTkLabel(self.MainFrame, text=f'{hostname}: {status}', text_color='#059669', fg_color='white', corner_radius=10, font=self.mediumFont)
        
        MessageLabel.place(relx=0.81, rely=0.43, anchor=ctk.CENTER)
        MessageLabel.after(2000, lambda: MessageLabel.place_forget())


    def discover(self):
        client = self.ClientListBox.get()
        if client == None:
            msg = 'Please select any client to discover!'
            MessageLabel = ctk.CTkLabel(self.MainFrame, text=msg, text_color='white', font=self.smallFont)
            MessageLabel.place(relx=0.81, rely=0.43, anchor=ctk.CENTER)
            MessageLabel.after(2000, lambda: MessageLabel.place_forget())
        else:
            hostname = client.split('\t')[-1]
            repoLabel = ctk.CTkLabel(self.MainFrame, text="Repository of " + hostname, text_color='black', fg_color='#92f5ac', corner_radius=10, font=self.mediumFont)
            repoLabel.place(relx=0.81, rely=0.5, anchor=ctk.CENTER)
            listFile = self.server.discover(hostname)
            if self.RepoList.size():
                self.RepoList.delete(0,'END')
            for file in listFile:
                self.RepoList.insert('END',file)


    def update_client_listbox(self):
        if self.ClientListBox.size():
            self.ClientListBox.delete(0,'END')
        for hostname in self.server.connectedClient:
            value = self.server.connectedClient[hostname][0] + '\t\t\t' + hostname
            self.ClientListBox.insert('END', value)


    def start_server(self):
        self.server.start()



if __name__ == '__main__':
    UI = ServerUI()
    UI.app.mainloop()
