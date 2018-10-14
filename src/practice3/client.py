import socket, select, string, sys

# ANSI escape sequences for colored text
class bcolors:
    RED = '\33[31m'
    YELLOW = '\33[33m'
    BLUE = '\33[34m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'
    
#Helper function (formatting)
def display() :
	you= bcolors.YELLOW+ bcolors.BOLD +" You: "+ bcolors.ENDC
	sys.stdout.write(you)
	sys.stdout.flush()

def main():
    if len(sys.argv)<2:
        host = raw_input("Enter host ip address: ")
    else:
        host = sys.argv[1]

    port = 5001
    
    #asks for user name
    name=raw_input(bcolors.BLUE + bcolors.BOLD + "CREATING NEW ID:\n Enter username: " + bcolors.ENDC)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    
    # connecting host
    try :
        s.connect((host, port))
    except :
        print bcolors.RED + bcolors.BOLD + "Can't connect to the server" + bcolors.ENDC
        sys.exit()

    #if connected
    s.send(name)
    display()
    while 1:
        socket_list = [sys.stdin, s]
        
        # Get the list of sockets which are readable
        rList, wList, error_list = select.select(socket_list , [], [])
        
        for sock in rList:
            #incoming message from server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print bcolors.RED + bcolors.BOLD + '\rDISCONNECTED!!\n' + bcolors.ENDC
                    sys.exit()
                else :
                    sys.stdout.write(data)
                    display()
        
            #user entered a message
            else :
                msg=sys.stdin.readline()
                s.send(msg)
                display()

if __name__ == "__main__":
    main()