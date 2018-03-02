#!/usr/bin/env python3

# Import the libraries we need
import sys
sys.path.insert(0, "./references/pixy")

#from references.pixy import pixy_init
from pixy import *
from ctypes import *
import time
from references import UltraBorg3


class Blocks (Structure):
    _fields_ = [("type", c_uint),
                ("signature", c_uint),
                ("x", c_uint),
                ("y", c_uint),
                ("width", c_uint),
                ("height", c_uint),
                ("angle", c_uint)]


class Vision():
    """Vision class to handle PixyCam Data"""

    def __init__(self, steering, ultrasonics):
        super(Vision, self).__init__()
        self.__steering = steering
        self.__ultrasonics = ultrasonics

    def watch(self):
        try:
            # Initialize Pixy Interpreter thread #
            pixy_init()

            blocks = BlockArray(100)
            frame = 0

            # Wait for blocks #
            while 1:
                count = pixy_get_blocks(100, blocks)
                if count > 0:
                    # Blocks found #
                    print('frame %3d:' % (frame))
                    frame = frame + 1
                    for index in range(0, count):
                        print('[BLOCK_TYPE=%d SIG=%d X=%3d Y=%3d WIDTH=%3d HEIGHT=%3d]' % (
                            blocks[index].type, blocks[index].signature, blocks[index].x, blocks[index].y, blocks[index].width, blocks[index].height))

        except KeyboardInterrupt:
            raise
        except:
            raise
