import socket
import select
import sys
import threading
from colorama import Fore, Back, Style

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IP_address = input("What IP address would you like to connect to? ")
if IP_address == "":
    print("Server IP required!")
    exit()

Port = input("And on which port? ")
if Port == "" or Port.isdigit() == False:
    print("Port is required!")
    exit()

server.connect((IP_address, int(Port)))

def receive_messages(server):

    try:
        data = server.recv(2048)
        while data:
            print(data.decode())
            data = server.recv(2048)
    except:
        server.close()

rt = threading.Thread(target=receive_messages,args=(server,))

rt.daemon = True

rt.start()

message = ""
while message != "exit":
    message = input()
    if message == "exit":
        print("Goodbye!")
    else:
        print("<You> {}".format(message))
    
    server.send(message.encode())

server.close()
