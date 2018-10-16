import socket, select, sys

# ANSI escape sequences for colored text
class TextColors:
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    RED = '\33[31m'
    GREEN = '\33[32m'
    YELLOW = '\33[33m'
    BLUE = '\33[34m'
    PURPLE = '\33[35m'

class Constants:
    RECV_BUFF = 1024
    LISTEN_BACKLOG = 10
    SERVER_WORKING = TextColors.GREEN + "SERVER WORKING" + TextColors.ENDC
    NAME_EXIST = "\r" + TextColors.RED + TextColors.BOLD + "Username already taken!\n" + TextColors.ENDC
    WELCOME_MSG = TextColors.GREEN + TextColors.BOLD + "Welcome to chat room. Enter 'tata' anytime to exit\n" + TextColors.ENDC

# Send message to all connected clients
def send_to_all (sendSock, servSock, message, connList):
    # Do not forward the message to server and sender
    for sock in connList:
        if sock != sendSock and sock != servSock:
            try:
                sock.send(message)
            except:
                sock.close()
                connList.remove(sock)

def main():
    # Get host and port number from arguments
    if len(sys.argv) < 3:
        print("usage: python3 ", sys.argv[0], "<host> <port>")
        sys.exit()
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    # Dictionary to store address corresponding to name
    name = ""
    record = {}

    # List of socket descriptors
    connList = []

    servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servSock.bind((host, port))
    servSock.listen(Constants.LISTEN_BACKLOG)

    # Add server socket to the list of readable connections
    connList.append(servSock)

    print(Constants.SERVER_WORKING)

    while True:
        # Get the lists of sockets with sockets in connected list
        readableList, writableList, errorList = select.select(connList, [], [])

        for sock in readableList:
            # New connection
            if sock == servSock:
                newConnSock, addr = servSock.accept()
                name = newConnSock.recv(Constants.RECV_BUFF)
                connList.append(newConnSock)
                record[addr] = ""

                # Check name duplication
                if name in record.values():
                    newConnSock.send(Constants.NAME_EXIST.encode('utf-8'))
                    del record[addr]
                    connList.remove(newConnSock)
                    newConnSock.close()
                    continue
                else:
                    record[addr] = name
                    print("Client (%s, %s) connected" % addr," [",record[addr].decode('utf-8'),"]")
                    newConnSock.send(Constants.WELCOME_MSG.encode('utf-8'))
                    join_msg = TextColors.GREEN + TextColors.ENDC + "\r "+ name.decode('utf-8') +" joined the conversation" + TextColors.ENDC + "\n"
                    send_to_all(newConnSock, servSock, join_msg.encode('utf-8'), connList)

            # Get message from a client
            else:
                # Data from client
                try:
                    data = sock.recv(Constants.RECV_BUFF).decode('utf-8')

                    # Get address of client sending the message
                    ip, port = sock.getpeername()
                    name = record[(ip, port)].decode('utf-8')

                    if data == "\n":
                        msg = "\r" + TextColors.RED + TextColors.BOLD + name + " left the conversation " + TextColors.ENDC + "\n"
                        send_to_all(sock, servSock, msg.encode('utf-8'), connList)
                        print("Client (%s, %s) is offline" % (ip, port)," [", name, "]")
                        del record[(ip, port)]
                        connList.remove(sock)
                        sock.close()
                        continue
                    
                    else:
                        data = data.rstrip()
                        msg = "\r" + TextColors.PURPLE + TextColors.BOLD + name + ": " + TextColors.ENDC + data + "\n"
                        send_to_all(sock, servSock, msg.encode('utf-8'), connList)

                # Abrupt user exit
                except:
                    ip, port = sock.getpeername()
                    name = record[(ip, port)].decode('utf-8')
                    msg = "\r" + TextColors.RED + TextColors.BOLD + name +" left the conversation unexpectedly" + TextColors.ENDC + "\n"
                    send_to_all(sock, servSock, msg.encode('utf-8'), connList)
                    print("Client (%s, %s) is offline (error)" % (ip, port)," [", name,"]\n")
                    del record[(ip, port)]
                    connList.remove(sock)
                    sock.close()
                    continue
    
    servSock.close()
    
if __name__ == '__main__':
    main()
