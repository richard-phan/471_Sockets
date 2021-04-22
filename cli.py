import os
import socket
import sys

from command import Command
from socket_utils import create_header, parse_header, recv


# total length of the header message
HEADER_LENGTH = 10

# creates the ephemeral socket
def connect_ephemeral(port):
    # create an ephemeral socket
    e_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connects the ephemeral socket to the cleint server
    e_socket.connect((SERVER_IP, E_PORT))

    return e_socket

# parses the command
def parse_command(cmd):
    # splits the command into the main command and argument
    cmds = cmd.split()
    cmd = cmds[0]
    arg = None

    if len(cmds) == 2:
        arg = cmds[1]

    return cmd, arg

# get command
def get(client_socket, e_socket, filename):
    # create the header
    header = create_header(len(filename), Command.GET)

    # send the header and filename
    client_socket.send(bytes(header + filename, 'utf-8'))

    # get the header
    header = client_socket.recv(HEADER_LENGTH).decode('utf-8')

    # parse the header
    file_size, cmd = parse_header(header)

    # error if file not found
    if cmd == Command.ERROR:
        print('File does not exist on server')
        return

    # receieve file data from server
    raw_data = recv(e_socket, file_size)

    # get filename from data
    filename = raw_data[:raw_data.index('*')]
    # get data from data
    data = raw_data[raw_data.index('*') + 1:]

    # write to file
    f = open(filename, 'w')
    f.write(data)
    f.close()

# put command
def put(client_socket, e_socket, filename):
    # open and read the file
    f = open(filename, 'r')
    data = f.read()

    # add asterisk as filename marker
    data = filename + "*" + data

    # create the header
    header = create_header(len(data), Command.PUT)

    # send the header to the server
    client_socket.send(bytes(header, 'utf-8'))

    # holds the current bytes sent to server
    bytes_sent = 0

    # continuously send data to the server until all bytes have been sent
    while bytes_sent != len(data):
        bytes_sent += e_socket.send(bytes(data[bytes_sent:], 'utf-8'))

# ls command
def ls(client_socket, e_socket):
    # create the header
    header = create_header(0, Command.LS)

    # sends the header to the server
    client_socket.send(bytes(header, 'utf-8'))

    # receive the header from the server
    header = recv(e_socket, HEADER_LENGTH)

    # parse the header data
    file_size, cmd = parse_header(header)

    # receive the data from the server
    data_raw = recv(e_socket, file_size)

    # split the data by spaces
    data = data_raw.split()
    # print data to console
    for d in data:
        print(d)

def quit(socket):
    # create the header
    header = create_header(0, Command.QUIT)

    # sends the header to the server
    socket.send(bytes(header, 'utf-8'))


# check if the command line arguments are correct
if len(sys.argv) < 3:
    print(f'USAGE python {sys.argv[0]} <SERVER IP> <SERVER PORT>')
    exit()

# initialize IP and PORT numbers
SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
E_PORT = SERVER_PORT + 1

# creates the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connects the client socket to the server
client_socket.connect((SERVER_IP, SERVER_PORT))

while True:
    # create ephemeral socket variable
    e_socket = None

    # gets the user input
    cmds = input('ftp>')

    # parses the user input
    cmd, arg = parse_command(cmds)

    # check if the command needs the empheral port
    if cmd != 'quit':
        # create ephemeral socket
        e_socket = connect_ephemeral(E_PORT)

    if cmd == 'get' and arg:
        get(client_socket, e_socket, arg)
        e_socket.close()
    elif cmd == 'put' and arg:
        put(client_socket, e_socket, arg)
    elif cmd == 'ls':
        ls(client_socket, e_socket)
    elif cmd == 'quit':
        quit(client_socket)
        client_socket.close()
        exit()
    else:
        print('Invalid command')

    e_socket.close()