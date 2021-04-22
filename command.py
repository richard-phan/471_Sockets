from enum import Enum

# command enum
class Command(Enum):
    NONE = 0
    GET = 1
    PUT = 2
    LS = 3
    QUIT = 4
    ERROR = 5
    OK = 6