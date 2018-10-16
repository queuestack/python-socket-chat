import socket, select, sys

class TextColors:
    # ANSI escape sequences for colored text
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    RED = '\33[31m'
    GREEN = '\33[32m'
    YELLOW = '\33[33m'
    BLUE = '\33[34m'
    PURPLE = '\33[35m'
class Constants:
    RECV_BUFF = 2 ** 12
    LISTEN_BACKLOG = 10
    SERVER_WORKING = TextColors.GREEN + "Server is now  working" + TextColors.ENDC
    NAME_EXIST = "\r" + TextColors.RED + TextColors.BOLD + "Username already exists!\n" + TextColors.ENDC
    WELCOME_MSG = TextColors.GREEN + TextColors.BOLD + "Welcome to this chat application. You can exit with Enter('\\n')\n" + TextColors.ENDC
def send_all (sendSock, servSock, message, connList):
    # Do not forward the message to server and sender
    for sock in connList:
        if sock != sendSock and sock != servSock:
            try:
                sock.send(message)
            except:
                if sock:
                    sock.close()
                connList.remove(sock)
def connect_client(sock, servSock, names, connList):
    newConnSock, addr = servSock.accept()
    name = newConnSock.recv(Constants.RECV_BUFF)
    connList.append(newConnSock)
    names[addr] = ""

    # Check name duplication
    if name in names.values():
        newConnSock.send(Constants.NAME_EXIST.encode('utf-8'))
        del names[addr]
        connList.remove(newConnSock)
        if newConnSock:
            newConnSock.close()
        return

    else:
        names[addr] = name
        print("(IP: %s, port: %s) connected" % addr," [name: ",names[addr].decode('utf-8'),"]")
        newConnSock.send(Constants.WELCOME_MSG.encode('utf-8'))
        join_msg = TextColors.GREEN + TextColors.ENDC + "\r "+ name.decode('utf-8') +" joined to chat" + TextColors.ENDC + "\n"
        send_all(newConnSock, servSock, join_msg.encode('utf-8'), connList)
        return
def recv_and_send_msg(sock, servSock, names, connList):
    # Data from client
    try:
        data = sock.recv(Constants.RECV_BUFF).decode('utf-8')

        # Get address of client sending the message
        ip, port = sock.getpeername()
        name = names[(ip, port)].decode('utf-8')

        if data == "\n":
            msg = "\r" + TextColors.RED + TextColors.BOLD + name + " left the conversation " + TextColors.ENDC + "\n"
            send_all(sock, servSock, msg.encode('utf-8'), connList)
            print("Client (%s, %s) is offline" % (ip, port)," [", name, "]")
            del names[(ip, port)]
            connList.remove(sock)
            if sock:
                sock.close()
            return
        
        else:
            data = data.rstrip()
            msg = "\r" + TextColors.PURPLE + TextColors.BOLD + name + ": " + TextColors.ENDC + data + "\n"
            send_all(sock, servSock, msg.encode('utf-8'), connList)
            return

    # Abrupt user exit
    except:
        ip, port = sock.getpeername()
        name = names[(ip, port)].decode('utf-8')
        msg = "\r" + TextColors.RED + TextColors.BOLD + name +" left the conversation unexpectedly" + TextColors.ENDC + "\n"
        send_all(sock, servSock, msg.encode('utf-8'), connList)
        print("Client (%s, %s) is offline (error)" % (ip, port)," [name: ", name,"]\n")
        del names[(ip, port)]
        connList.remove(sock)
        if sock:            
            sock.close()
        return
    
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
    names = {}

    # List of socket descriptors
    connList = []

    servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servSock.bind((host, port))
    servSock.listen(Constants.LISTEN_BACKLOG)

    # Add server socket to the list of readable connections
    connList.append(servSock)

    print(Constants.SERVER_WORKING)

    while True:
        try:
            # Get the lists of sockets with sockets in connected list
            readableList, writableList, errorList = select.select(connList, [], [])

            for sock in readableList:
                # Connect to new client if socket is server socket
                # Receive message from a client and sent the message to other clients
                connect_client(sock, servSock, names, connList) if sock == servSock else recv_and_send_msg(sock, servSock, names, connList)

        except KeyboardInterrupt:
            for sock in connList:
                if sock:
                    sock.close()
                
            sys.exit()
    
    if servSock:   
        servSock.close()

if __name__ == '__main__':
    main()
