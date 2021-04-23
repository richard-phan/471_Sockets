from command import Command

# total length of the header message
HEADER_LENGTH = 10

# creates the message header
# first 9 digits = total message size
# last digit = command type (Command enum)
def create_header(size, protocol):
    return '0' * ((HEADER_LENGTH - 1) - len(str(size))) + str(size) + str(protocol.value)

# splits the header into file size and Command enum
def parse_header(header):
    file_size = int(header[:-1])
    cmd = int(header[-1:])

    return file_size, Command(cmd)

# receives the data from the socket
def recv(socket, file_size):
    tmp_buffer = ''
    data = ''

    while len(data) != file_size:
        tmp_buffer = socket.recv(file_size)

        if not tmp_buffer:
            break
        
        data += tmp_buffer.decode('utf-8')

    return data