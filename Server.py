import socket
server = socket.socket()
server.bind(("192.168.182.243",5001))
server.listen()
conn, addr = server.accept()
print ("Connection from: " + str(addr))
while True:
   data = conn.recv(1024).decode()
   if not data:
      break
   data = str(data).upper()
   print (" from client: " + str(data))
   data = input("type message: ")
   conn.send(data.encode())
conn.close()