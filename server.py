import os
import socket

from command import Command
from socket_utils import create_header, parse_header, recv

# get command
def get(socket, filename):
    # initialize file
    f = None

    try:
        # open the file
        f = open(filename, 'r')
    except FileNotFoundError:
        # send error if file not found
        header = create_header(0, Command.ERROR)
        # send header to client
        socket.send(bytes(header, 'utf-8'))
        return

    # read the file data
    data = f.read()

    # append file name to data
    data = filename + '*' + data

    # create the header
    header = create_header(len(data), Command.NONE)
    # send the header to the client
    socket.send(bytes(header, 'utf-8'))

    # 
    bytes_sent = 0

    # continuously send data to the server until all bytes have been sent
    while bytes_sent != len(data):
        bytes_sent += socket.send(bytes(data[bytes_sent:], 'utf-8'))

# put command
def put(data):
    filename = raw_data[:raw_data.index('*')]
    data = raw_data[raw_data.index('*') + 1:]

    f = open(filename, 'w')
    f.write(data)
    f.close()

# ls command
def ls(socket):
    files = os.listdir('.')
    data = ''

    for f in files:
        data += f + ' '

    header = create_header(len(data), Command.NONE)
    socket.send(bytes(header, 'utf-8'))

    bytes_sent = 0

    # continuously send data to the server until all bytes have been sent
    while bytes_sent != len(data):
        bytes_sent += socket.send(bytes(data[bytes_sent:], 'utf-8'))

# initialize header length
HEADER_LENGTH = 10

# initialize PORT number
PORT = 1234

# create the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# binds the server socket to the IP and PORT
server_socket.bind(('', PORT))

# enable accepting of connections from the socket
server_socket.listen(1)

while True:
    print('Waiting for connections...')

    # accept a connection to the server
    conn_socket, addr = server_socket.accept()
    print(f'{addr[0]}:{addr[1]} has connected')

    # get the header from the client
    header = conn_socket.recv(HEADER_LENGTH).decode('utf-8')
    # parse the header from the client
    try:
        file_size, cmd = parse_header(header)
    except ValueError:
        continue

    if cmd == Command.GET:
        filename = recv(conn_socket, file_size)
        get(conn_socket, filename)
    elif cmd == Command.PUT:
        # receive data from the client
        raw_data = recv(conn_socket, file_size)
        put(raw_data)
    elif cmd == Command.LS:
        ls(conn_socket)
    elif cmd == Command.QUIT:
        conn_socket.close()
        print('Client socket has manually disconnected')