import os
import socket
import sys

sys.path.insert(1, '../utils')

from command import Command
# from socket_utils import create_header, parse_header, recv
from socket_utils import create_header, parse_header, recv

# get command
def get(main_socket, e_socket, filename):
    # initialize file
    f = None

    try:
        # open the file
        f = open(filename, 'r')
    except FileNotFoundError:
        # send error if file not found
        header = create_header(0, Command.ERROR)
        # send header to client
        main_socket.send(bytes(header, 'utf-8'))
        return False

    # read the file data
    data = f.read()

    # append file name to data
    data = filename + '*' + data

    # create the header
    header = create_header(len(data), Command.NONE)
    # send the header to the client
    main_socket.send(bytes(header, 'utf-8'))

    # 
    bytes_sent = 0

    # continuously send data to the server until all bytes have been sent
    while bytes_sent != len(data):
        bytes_sent += e_socket.send(bytes(data[bytes_sent:], 'utf-8'))

    return True

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
E_PORT = 1235

# create the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# binds the server socket to the IP and PORT
server_socket.bind(('', PORT))
# enable accepting of connections from the socket
server_socket.listen(1)

# create the ephemeral socket
e_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# binds the ephemeral socket to the IP and PORT
e_socket.bind(('', E_PORT))
# enable accepting of connections from the socket
e_socket.listen(1)

# main loop
while True:
    print('Waiting for connections...')

    # accept a connection to the server
    main_socket, addr = server_socket.accept()
    print(f'{addr[0]}:{addr[1]} has connected')

    while main_socket:
        # get the header from the client
        header = main_socket.recv(HEADER_LENGTH).decode('utf-8')

        # parse the header from the client
        try:
            data_size, cmd = parse_header(header)
        except ValueError:
            continue

        # check if the command needs the empherical port
        if cmd != Command.QUIT:
            # accept a connection through the ephemeral socket
            conn_socket, addr = e_socket.accept()
            print(f'{addr[0]}:{addr[1]} has connected on the ephemeral port')

        if cmd == Command.GET:
            filename = recv(main_socket, data_size)
            success = get(main_socket, conn_socket, filename)
            if success:
                print("GET Success")
            else:
                print("GET Failure")
        elif cmd == Command.PUT:
            # receive data from the client
            raw_data = recv(conn_socket, data_size)
            put(raw_data)
            print("PUT Success")
        elif cmd == Command.LS:
            ls(conn_socket)
            print("LS Success")
        elif cmd == Command.QUIT:
            main_socket.close()
            main_socket = None
            addr = None
            print('Client socket disconnected')
            continue
        
        conn_socket.close()
        print('Ephemeral socket closed')