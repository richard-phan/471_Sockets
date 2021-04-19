import os
import socket
import sys

from command import Command
from socket_utils import create_header, parse_header, recv


# total length of the header message
HEADER_LENGTH = 10

# creates the ephemeral socket
def create_ephemeral(port):
    ephemeral = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ephemeral.bind(('', port))

    return ephemeral

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
def get(socket, filename):
    # create the header
    header = create_header(len(filename), Command.GET)

    # send the header and filename
    socket.send(bytes(header + filename, 'utf-8'))

    # get the header
    header = socket.recv(HEADER_LENGTH).decode('utf-8')

    # parse the header
    file_size, cmd = parse_header(header)

    # error if file not found
    if cmd == Command.ERROR:
        print('File does not exist on server')
        return

    # receieve file data from server
    raw_data = recv(socket, file_size)

    # get filename from data
    filename = raw_data[:raw_data.index('*')]
    # get data from data
    data = raw_data[raw_data.index('*') + 1:]

    # write to file
    f = open(filename, 'w')
    f.write(data)
    f.close()

# put command
def put(socket, filename):
    # open and read the file
    f = open(filename, 'r')
    data = f.read()

    # add asterisk as filename marker
    data = filename + "*" + data

    # create the header
    header = create_header(len(data), Command.PUT)

    # send the header to the server
    socket.send(bytes(header, 'utf-8'))

    # holds the current bytes sent to server
    bytes_sent = 0

    # continuously send data to the server until all bytes have been sent
    while bytes_sent != len(data):
        bytes_sent += socket.send(bytes(data[bytes_sent:], 'utf-8'))

# ls command
def ls(socket):
    # create the header
    header = create_header(0, Command.LS)

    # sends the header to the server
    socket.send(bytes(header, 'utf-8'))

    # receive the header from the server
    header = recv(socket, HEADER_LENGTH)

    # parse the header data
    file_size, cmd = parse_header(header)

    # receive the data from the server
    data = recv(socket, file_size)

    return data.split()

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

while True:
    # creates the client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connects the client socket to the server
    client_socket.connect((SERVER_IP, SERVER_PORT))
    # gets the user input
    cmds = input('ftp>')

    # parses the user input
    cmd, arg = parse_command(cmds)

    if cmd == 'get' and arg:
        get(client_socket, arg)
    elif cmd == 'put' and arg:
        put(client_socket, arg)
    elif cmd == 'ls':
        data = ls(client_socket)
        
        for d in data:
            print(d)
    elif cmd == 'quit':
        quit(client_socket)
        client_socket.close()
        exit()
    else:
        print('Invalid command')

    client_socket.close()