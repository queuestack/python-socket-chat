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

class Texts:
    USAGE = "usage: python3 %s <host> <port"
    START_SRV = TextColors.GREEN + "Chat Server started on port %s" + TextColors.ENDC
    NAME_EXIST = TextColors.RED + TextColors.BOLD + "\r Username already exists!\n" + TextColors.ENDC
    WELCOME_MSG = TextColors.GREEN + TextColors.BOLD + "\r Welcome to this chat application. You can exit with Enter('\\n')\n" + TextColors.ENDC
    CONN_MSG = TextColors.BLUE + TextColors.BOLD + "\rConnected to the chat server (%s %s online)\n" + TextColors.ENDC
    JOIN_MSG = TextColors.BLUE + TextColors.BOLD + "\r> New user %s:%s entered (%s %s online)\n" + TextColors.ENDC
    EXIT_MSG = TextColors.RED + TextColors.BOLD + "\r< The user %s:%s left (%s %s online)\n" + TextColors.ENDC
    SEND_MSG = TextColors.PURPLE + TextColors.BOLD + "\r[%s:%s]: %s\n" + TextColors.ENDC
    USER = "user"
    USERS = "users"
    KEY_INTER = "\rKeyboardInterrupt\n"

class Constants:
    RECV_BUFF = 2 ** 12
    LISTEN_BACKLOG = 10
    NUM_SERVER = 1
    NUM_LEAVING_CLIENT = 1

def send_all (sendSock, servSock, message, connList):
    # Send message to connected sockets except server and sender
    for sock in connList:
        if sock != sendSock and sock != servSock:
            try:
                sock.send(message)
            except:
                if sock:
                    sock.close()
                connList.remove(sock)

def connect_client(sock, servSock, connList):
    # Connect to client
    newConnSock, addr = servSock.accept()
    ip, port = addr
    connList.append(newConnSock)
    
    # Send connection message to other clients
    conn_msg = make_conn_msg(connList) 
    join_msg = make_join_msg(ip, port, connList)

    newConnSock.send(conn_msg.encode('utf-8'))
    send_all(newConnSock, servSock, join_msg.encode('utf-8'), connList)
    print(join_msg)
    return

def make_conn_msg(connList):
    # Get current user numbers and make connection message
    nUser = len(connList) - Constants.NUM_SERVER
    user = Texts.USER if nUser == 1 else Texts.USERS
    return Texts.CONN_MSG % (nUser, user)

def make_join_msg(ip, port, connList):
    # Get current user numbers and make join message
    nUser = len(connList) - Constants.NUM_SERVER
    user = Texts.USER if nUser == 1 else Texts.USERS
    return Texts.JOIN_MSG % (ip, port, nUser, user)

def make_leave_msg(ip, port, connList):
    # Get current user numbers and make leave message
    nUser = len(connList) - Constants.NUM_SERVER - Constants.NUM_LEAVING_CLIENT
    user = Texts.USER if (nUser == 1 or nUser == 0) else Texts.USERS
    return Texts.EXIT_MSG % (ip, port, nUser, user)

def recv_and_send_msg(sock, servSock, connList):
    # Receive message from a client and send the message to the other clients
    try:
        # Get data
        data = sock.recv(Constants.RECV_BUFF).decode('utf-8')

        # Get address of client sending the message
        ip, port = sock.getpeername()
        
        if data == "\n":
            # Client exits the chat room when the data is new line
            # Send closing connection message to other clients and server
            msg = make_leave_msg(ip, port, connList)
            send_all(sock, servSock, msg.encode('utf-8'), connList)
            print(msg)

            # Close connection
            connList.remove(sock)            
            if sock:
                sock.close()
            return
        
        else:
            # Send message to the other clients and server
            data = data.rstrip()
            msg = Texts.SEND_MSG % (ip, port, data)
            send_all(sock, servSock, msg.encode('utf-8'), connList)
            print(msg)
            return


    except:
        # Handle error
        ip, port = sock.getpeername()

        # Send error message to other clients and server
        msg = make_leave_msg(ip, port, connList) + " (error) "
        send_all(sock, servSock, msg.encode('utf-8'), connList)
        print(msg)

        # Close connection
        connList.remove(sock)
        if sock:            
            sock.close()
        return
    
def main():
    # Get host and port number from arguments
    if len(sys.argv) < 3:
        print(Texts.USAGE % sys.argv[0])
        sys.exit()
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    # List of socket
    connList = []

    # Open server socket and bind it to input ip, port
    servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servSock.bind((host, port))
    servSock.listen(Constants.LISTEN_BACKLOG)

    # Add server socket to the list of socket
    connList.append(servSock)

    # Print server start message
    print(Texts.START_SRV % port )

    while True:
        try:
            # Get the lists of sockets with sockets from connected sockets
            readableList, writableList, errorList = select.select(connList, [], [])

            for sock in readableList:
                # Connect to new client if readable socket is server socket
                # Receive message from a client and send the message to other clients if readable socket is client socket
                connect_client(sock, servSock, connList) if sock == servSock else recv_and_send_msg(sock, servSock, connList)

        except KeyboardInterrupt:
            # Handle Ctrl + C
            # Close socket server before exiting the process
            for sock in connList:
                if sock:
                    sock.close()
            
            print(Texts.KEY_INTER)
            sys.exit()
    
    if servSock:
        servSock.close()

if __name__ == '__main__':
    main()
