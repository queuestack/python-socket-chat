import socket, sys, select
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))
while True:
  sr, sw, se = select.select([sys.stdin, sock], [], [])
  for s in sr:
    if s == sock:
      data = s.recv(1024)
      print(data)
    else:
      sock.send(input())
