import socket, select, string, sys

# ANSI escape sequences for colored text
class TextColors:
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  RED = '\33[31m'
  YELLOW = '\33[33m'
  BLUE = '\33[34m'

class Constants:
  SHOW_YOU = TextColors.YELLOW + TextColors.BOLD + " You: " + TextColors.ENDC
  ASK_NAME = TextColors.BLUE + TextColors.BOLD + "Enter username: " + TextColors.ENDC
  TIMEOUT_TIME = 2
  CONNECT_ERROR = TextColors.RED + TextColors.BOLD + "Fail to connect to the server" + TextColors.ENDC
  RECV_BUFSIZE = 1024
  DISCONNECTION = TextColors.RED + TextColors.BOLD + "\r Connection is closed \n" + TextColors.ENDC


# Connect to server
def connect(sock, host, port):
  try:
    sock.connect((host, port))
  except:
    print(Constants.CONNECT_ERROR)
    sys.exit()

# Display user name on console
def display():
  sys.stdout.write(Constants.SHOW_YOU)
  sys.stdout.flush()

def main():
  if len(sys.argv) < 3:
    print("usage: python3 ", sys.argv[0], "<host> <port>")
    sys.exit()
  else:
    host = sys.argv[1]
    port = int(sys.argv[2])

  # Asks for user nickname
  name = input(Constants.ASK_NAME)
  connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  connSock.settimeout(2)

  # Connect to server with host and port number
  connect(connSock, host, port)

  # Send connection message to server
  connSock.send(name.encode('utf-8'))

  while True:
    # Get the lists of sockets with sys.stdin and connected socket as an inputs
    readableList, writableList, errorList = select.select([sys.stdin, connSock], [], [])
    
    for sock in readableList:
      # Receive message from server
      if sock == connSock:
        data = sock.recv(Constants.RECV_BUFSIZE)
        if not data:
          print(Constants.DISCONNECTION)
          sys.exit()
        else:
          sys.stdout.write(data.decode('utf-8'))
          display()
      
      # Send message to server
      else:
        message = sys.stdin.readline()
        connSock.send(message.encode('utf-8'))
        display()

if __name__ == "__main__":
  main()