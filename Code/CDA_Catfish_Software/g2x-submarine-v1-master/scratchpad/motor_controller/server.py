#!/usr/bin/python3
import socket                                         


# get local machine name
# host = socket.gethostname()                           
host = "0.0.0.0"
port = 9999                                           

# create a socket object and bind to specified host/port
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
serversocket.bind((host, port))                                  

# queue up to 5 requests
serversocket.listen(5)                                           

while True:
    # establish a connection
    clientsocket,addr = serversocket.accept()

    while True:
        data = clientsocket.recv(1024).decode()
        if not data:
            break

        print("Got a connection from {0}: {1}".format(str(addr), data))

        msg = "Received {0} bytes\r\n".format(len(data))
        clientsocket.send(msg.encode('ascii'))

    clientsocket.close()