#!/usr/bin/env python3

# Import the libraries we need
from __future__ import division
import sys
import time
import math

sys.path.insert(0, "./references/pixy")
from pixy import *
from ctypes import *
from references import UltraBorg3
from telemetry import Telemetry


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
        self.__logger = Telemetry(self.__class__.__name__, "csv").get()
        self.__logger.info(
            'Frame, Block Type, Signature, X, Y, Width, Height, Size, Angle, Distance, Factor')
        self.__objectHeight = 46  # mm
        self.__focalLength = 2.4  # mm

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
                    #print('frame %f:' % (frame))
                    frame = frame + 1
                    for index in range(0, count):
                        btype = blocks[index].type
                        bsign = blocks[index].signature
                        bx = blocks[index].x
                        by = blocks[index].y
                        bwidt = blocks[index].width
                        bheig = blocks[index].height
                        bsize = bwidt * bheig
                        angle = blocks[index].angle
                        bdist = (self.__objectHeight *
                                 self.__focalLength) / bheig
                        factor = 0
                        if(bsize > 1000):
                            if(bx < 180):
                                factor = -1 * (0.9 / 180) * abs(180 - bx)
                                self.__steering.steerAbsolute(factor)
                            elif(bx > 180):
                                factor = (0.9 / 180) * abs(180 - bx)
                                self.__steering.steerAbsolute(factor)
                            else:
                                self.__steering.reset()

                        strOp = ('%d, %d, %d, %f, %f, %f, %f, %f, %f, %f, %f' % (
                            frame, btype, bsign, bx, by, bwidt, bheig, bsize, angle, bdist, factor))
                        self.__logger.info(strOp)

        except KeyboardInterrupt:
            raise
        except:
            raise
