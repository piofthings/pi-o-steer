#!/usr/bin/env python3

# Import the libraries we need
# from __future__ import division
import sys
import time
import math
import traceback

sys.path.insert(0, "./references/pixy")
from pixy import *
from ctypes import *
from references import UltraBorg3
from telemetry import Telemetry
from pan_tilt_controller import PanTiltController
from vision import VisionAttributes
from vision import BlockPosition
from vision import Blocks


class StraightLineVision():
    """Vision class to handle PixyCam Data"""
    COLOUR_WHITE = 1  # White
    COLOUR_RED = 2  # Red
    COLOUR_BLUE = 3  # Blue
    COLOUR_YELLOW = 4  # Yellow
    COLOUR_GREEN = 5  # Green
    COLOUR_UNKNOWN = -99  # Default

    RED_TURN_POSITION = 0
    BLUE_TURN_POSITION = 1
    YELLOW_TURN_POSITION = 2
    GREEN_TURN_POSITION = 3

    PIXY_RES_X = 320
    PIXY_RES_Y = 200

    def __init__(self, steering, motors):
        super(StraightLineVision, self).__init__()
        self.__steering = steering
        self.__motors = motors

        self.__logger = Telemetry(self.__class__.__name__, "csv").get()
        self.__logger.info(
            'Frame, Block Type, Signature, X, Y, Width, Height, Size, Angle, Distance, Factor, MovingFor, Pan Position, Action')
        self.__objectHeight = 46  # mm
        self.__focalLength = 2.4  # mm
        pixy_init()

    def initialise(self, visionAttribs, ptc):
        self.__visionAttributes = visionAttribs
        self.__tilt_position = self.__visionAttributes.startTiltAngle
        self.__pan_position = self.__visionAttributes.startPanAngle
        self.__prev_pan_position = self.__pan_position
        self.__pan_tilt_controller = ptc
        self.__pan_tilt_controller.pan_absolute(self.__pan_position)
        self.__pan_tilt_controller.tilt_absolute(
            self.__tilt_position)
        time.sleep(0.01)

    def track(self, colour_code):
        found = True
        blocks = BlockArray(100)
        pan_dir = 'straight'
        self.__steering.reset()
        while found == True:
            current_block_position = BlockPosition()
            frame = -1
            btype = -1
            angle = -1
            bdist = -1
            frame = frame + 1
            count = pixy_get_blocks(100, blocks)
            strOp = ""
            if count > 0:
                for index in range(0, count):
                    current_block_position.colour = blocks[index].signature
                    btype = blocks[index].type
                    current_block_position.x = blocks[index].x
                    current_block_position.y = blocks[index].y
                    current_block_position.width = blocks[index].width
                    current_block_position.height = blocks[index].height
                    current_block_position.size = current_block_position.width * \
                        current_block_position.height
                    angle = blocks[index].angle
                    bdist = (self.__objectHeight *
                             self.__focalLength) / current_block_position.height
                    if (int(current_block_position.colour) == int(colour_code)):
                        if current_block_position.x < ((self.PIXY_RES_X / 2) * 0.9):
                            pan_dir = 'left'
                        elif current_block_position.x > ((self.PIXY_RES_X / 2) + (self.PIXY_RES_X / 2 * 0.1)):
                            pan_dir = 'right'
                        else:
                            pan_dir = 'straight'
                        if((current_block_position.size > self.__visionAttributes.targetMinSize)
                           and (current_block_position.x > ((self.PIXY_RES_X / 2) - (current_block_position.width)))
                           and (current_block_position.x < ((self.PIXY_RES_X / 2) + (current_block_position.width)))):
                            status = "Found colour " + \
                                str(current_block_position.colour)
                            centered = True
                            pan_dir = self.__pan(pan_dir)
                            self.__motors.move(
                                1, 1, self.__visionAttributes.topSpeed, True)
                        else:
                            status = "Found colour but position not correct| pan: " + pan_dir
                            centered = False
                            pan_dir = self.__pan(pan_dir)

                        action = pan_dir
                        time.sleep(0.01)

                    else:
                        status = "Colour Not Matched| pan:" + pan_dir
                        action = "tracking"

            else:
                status = "Pixy didn't get anything" + \
                    " | pan:" + pan_dir
                found = False

            strOp = ('%d, %d, %d, %f, %f, %f, %f, %f, %f, %f, %s, %d, %f, %s' % (
                frame, btype, current_block_position.colour, current_block_position.x, current_block_position.y, current_block_position.width, current_block_position.height, current_block_position.size, angle, bdist, status, colour_code, self.__pan_position, pan_dir))
            self.__logger.info(strOp)
        #current_block_position.centered = centered
        return current_block_position

    def __pan(self, pan_dir, steer=True):
        if pan_dir == 'left':
            new_pan_position = self.__pan_position + \
                (self.__pan_tilt_controller.abs_pan_per_degree * 2)
            if self.__pan_position > self.__visionAttributes.maxPanAngle:
                pan_dir = 'right'
                self.__pan_position = 0

        elif pan_dir == 'right':
            self.__pan_position = self.__pan_position - \
                (self.__pan_tilt_controller.abs_pan_per_degree * 2)

            if self.__pan_position < self.__visionAttributes.minPanAngle:
                pan_dir = 'left'
                self.__pan_position = 0
        else:
            self.__pan_position = 0

        if (self.__pan_position < self.__visionAttributes.maxPanAngle) and (self.__pan_position > self.__visionAttributes.minPanAngle):
                # self.__pan_tilt_controller.pan_absolute(
                #     self.__pan_position)

            if steer == True:
                self.__steering.steerAbsolute(
                    self.__pan_position * -2.0)

        return pan_dir

    def dispose(self):
        pixy_close()
