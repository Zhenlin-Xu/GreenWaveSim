# Pygame - color
class Color(object):
    """
    An Enum class to represent common RGB 3-channel colors
    """
    DARK_RED = (256,0,   0)
    RED   = (255,  21,  21)
    YELLOW= (128, 128,   0)
    GREEN = (0  , 128,   0)
    LIGHT_GREEN = (21, 128, 21)
    BLUE  = ( 21,  21, 255)
    LIGHT_BLUE = (21, 21, 128)
    WHITE = (255, 255, 255)
    BLACK = (0  ,   0,   0)
    PINK  = (255, 105, 180)
    GREY  = (200, 200, 200)

# Terminal logging -color
from termcolor import colored

def logging(msg:str,
            color:str):
    print(colored(msg, color))