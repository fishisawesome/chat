import socket
import threading
from datetime import datetime
from colorama import Fore, Back, Style

list_of_clients = []
messages = []
threads = []

def save_messages(messages, filename="logs.txt"):
    textfile = open(filename, "w")
    for element in messages:
        textfile.write(element + "\n")

    textfile.close()

def get_message_time():
    return datetime.today().strftime('%Y-%m-%d %H:%M:%S')

def get_client_info(conn):
    peer_name = conn.getpeername()
    return "{}:{}".format(peer_name[0],peer_name[1])

def chat_log(message_to_send):
    message_time = get_message_time()
    message = "[{}] {}".format(message_time, message_to_send)
    print(message)
    messages.append(message)

    return message

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


IP_address = input("What IP address would you like to use? ")
if IP_address == "":
    print("Server IP required!")
    exit()

Port = input("And on which port? ")
if Port == "" or Port.isdigit() == False:
    print("Port is required!")
    print("Port is required!")
    exit()

server.bind((IP_address, int(Port)))
server.listen(100)

message_to_send = "Server running at {}:{}".format(IP_address, Port)
chat_log(message_to_send)

def clientthread(conn, addr):

    conn.send("Welcome to this chatroom!".encode())
    username = "<{}>".format(get_client_info(conn))
    message_to_send = "{} has joined the chatroom.".format(username)

    chat_log(message_to_send)
    
    broadcast(message_to_send, conn)
    
    keep_alive = True

    while keep_alive:
        message = conn.recv(2048)
        message = message.decode()
        if message:
            message = message.strip()
            if message == "exit":
                
                message_to_send = "<{}> has left the chat.".format(get_client_info(conn))
                chat_log(message_to_send)
                remove(conn)
                keep_alive = False

            else:
                message_received = 'Received "{}" from {}'.format(message, username)
                chat_log(message_received)
                message_to_send = "{} {}".format(username, message)
                broadcast(message_to_send, conn)

        else:
            remove(conn)
            keep_alive = False


    active_threads = threading.active_count()
    if active_threads == 2:
        answer = input("All clients have left. Save history? (Y/n) ")
        if "y" in answer.lower():
            print("Saving...")
            save_messages(messages)

        messages.clear()
        print("Waiting for new clients...")


def broadcast(message, connection):
    for clients in list_of_clients:
        if clients!=connection:
            try:

                clients.send(message.encode())

                message_to_send = "Message sent to <{}>".format(get_client_info(clients))
                chat_log(message_to_send)

            except:
                #  If one client disconnects, the other is notified if trying to send a message to the disconnected party.
                # Should send message to "connection" that it is unable to send to this specific client because it has disconnected
                # connection.send("X Client is no longer connected")
                clients.close()
                remove(clients)

def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)



while True:

    conn, addr = server.accept()

    list_of_clients.append(conn)

    t = threading.Thread(target=clientthread, args=(conn,addr))
    t.daemon = True
    t.start()


conn.close()
server.close()
