import socket, sys, select, string

class TextColors:
# ANSI escape sequences for colored text
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	RED = '\33[31m'
	YELLOW = '\33[33m'
	BLUE = '\33[34m'

class Texts:
	SHOW_YOU = TextColors.YELLOW + TextColors.BOLD + "[You]: " + TextColors.ENDC
	CONNECT_ERROR = TextColors.RED + TextColors.BOLD + "\r You can not connect to the server, check IP and host \n" + TextColors.ENDC
	DISCON_MSG = TextColors.RED + TextColors.BOLD + "\r< You have been disconnected \n" + TextColors.ENDC
	KEY_INTER = "\rKeyboardInterrupt\n"

class Constants:
	TIMEOUT_TIME = 2
	RECV_BUFSIZE = 2 ** 12

def connect(sock, host, port):
	# Connect to server
	try:
		sock.connect((host, port))
	except:
		print(Texts.CONNECT_ERROR)
		sys.exit()

def recv_msg(sock):
	# Recieve message from server
	data = sock.recv(Constants.RECV_BUFSIZE)
	if not data:
		print(Texts.DISCON_MSG)
		if sock:
			sock.close()
		sys.exit()
	else:
		sys.stdout.write(data.decode('utf-8'))
		display_you()

def send_msg(sock):
	# Send message from client
	message = sys.stdin.readline()
	sock.send(message.encode('utf-8'))
	display_you() 

def display_you():
	# Display 'YOU' on console
	sys.stdout.write(Texts.SHOW_YOU)
	sys.stdout.flush()

def run_client(connSock):
	# Get the lists of sockets with sys.stdin and connected socket as an inputs
	try:
		readableList, writableList, errorList = select.select([sys.stdin, connSock], [], [])
	
		for sock in readableList:
			# Receive message from server if readable socket is connected socket
			# Send message to server if readable socket is stdin
			recv_msg(connSock) if sock == connSock else send_msg(connSock)
		

	except KeyboardInterrupt:
		# Handle Ctrl + C
		connSock.send(b"\n")
		connSock.close()

		print(Texts.KEY_INTER)
		sys.exit()	

def main():
	# Get host and port number from arguments
	if len(sys.argv) < 3:
		print("usage: python3 ", sys.argv[0], "<host> <port>")
		sys.exit()
	else:
		host = sys.argv[1]
		port = int(sys.argv[2])

	# Create TCP socket and set timeout
	connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connSock.settimeout(Constants.TIMEOUT_TIME)

	# Connect to server with host and port number
	connect(connSock, host, port)

	while True:
		# Receive message from other clients
		# Send sys.stdin to other clients
		run_client(connSock)

if __name__ == "__main__":
  	main()