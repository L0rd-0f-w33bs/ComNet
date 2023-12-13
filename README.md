
# File-sharing application
# Introduction
File-sharing application is a console-based application that facilitates communication between multiple users over a LAN, allowing users to exchange files in real-time.

## Table of content

- [Introduction](#introduction)
- [Features](#features)
- [Usage](#usage)
## Features
File-sharing application provides the following features:

1. Client can register their accounts with unique hostnames.
2. Client can log in and log out of the application.
3. Server can discover the list of local files of all users.
4. Client can inform the server as to what files are contained by user without transmitting file data.
5. Multiple clients connect to a server and they can download files from each other.

## Usage

To use this application, users only need to run the clientUI.exe file (as a client) and the serverUI.exe file (as a server).

For the client interface, first, users need to enter the IP address of the server they want to connect to, along with their hostname.
Note that the hostname must be a string of characters written together and does not contain spaces.
After successful login, users will be transferred to the main interface for the client.

1. For server:

The interface for the server has two main areas.

The left area is used to display a list of clients that have connected to the server. This list includes their IP addresses and hostnames.
In addition, there is a reload button at the top with the task of updating information about new clients that have been added to the system.
Therefore, to ensure accuracy, it is necessary to often click on the reload icon to update.

The right one is the functional area of the server. There are two main functions, namely: Ping - to check whether the user is online,
and Discover - to collect all the names of the files in the repository of the selected client.
To use these two functions, first select a client in the left window, then click on the function button you want.

2. For client:

