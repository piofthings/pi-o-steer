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
    COLOR_RED = 1  # Red
    COLOR_GREEN = 2  # Green
    COLOR_YELLOW = 3  # Yellow
    COLOR_BLUE = 4  # Blue
    panServoRate = 1.0 / 270
    tiltPosition = -0.1
    __biggestBlockInFrame = dict()

    def __init__(self, steering, ultrasonics, motors):
        super(Vision, self).__init__()
        self.__steering = steering
        self.__ultrasonics = ultrasonics
        self.__motors = motors
        self.__logger = Telemetry(self.__class__.__name__, "csv").get()
        self.__minSize = 100
        self.__maxSize = 10000

        self.__logger.info(
            'Frame, Block Type, Signature, X, Y, Width, Height, Size, Angle, Distance, Factor, MovingFor, Pan Position, Action')
        self.__objectHeight = 46  # mm
        self.__focalLength = 2.4  # mm
        self.__minPan = -0.95
        self.__maxPan = 1.0
        self.__panPosition = 0
        pixy_init()
        self.__ultrasonics.ub.SetServoPosition2(0)
        self.__ultrasonics.ub.SetServoMaximum2(5000)
        self.__ultrasonics.ub.SetServoMinimum2(1000)

    def seek(self, colorCode):
        self.__ultrasonics.ub.SetServoPosition2(self.__panPosition)
        self.__ultrasonics.ub.SetServoPosition1(self.tiltPosition)
        detected = False
        frame = 0

        self.__panPosition = self.__maxPan
        self.__ultrasonics.ub.SetServoPosition2(self.__panPosition)
        while 1:
            detectedInitialSize = self.search(colorCode)
            reached = self.approach(detectedInitialSize, colorCode)
            return

    def approach(self, detectedInitialSize, colorCode):
        # TODO: Once the ball is found search and steer appropriately.
        reached = False
        blocks = BlockArray(100)
        frame = 0
        while reached == False:
            try:
                if('color' in self.__biggestBlockInFrame):
                    if (self.__biggestBlockInFrame['color'] == colorCode):
                        print('color match')

                        if(self.__biggestBlockInFrame['bsize'] > self.__minSize
                           and self.__biggestBlockInFrame['bsize'] < self.__maxSize):
                            print('size match')
                            self.__steering.steerAbsolute(0)

                        else:
                            self.__motors.move(1, 1, 0)

                            print('size mis-match')

                        if(self.__biggestBlockInFrame['bsize'] >= self.__maxSize):
                            self.__motors.move(1, 1, 0)

                            reached = True
                        else:

                            reached = False
                    else:
                        self.__motors.move(1, 1, 0)
                else:
                    self.__motors.move(1, 1, 0)

                count = pixy_get_blocks(100, blocks)
                if count > 0:

                    # Blocks found #
                    frameKey = 'frame' + str(frame)

                    # self.__biggestBlockInFrame = {frameKey: 0}
                    for index in range(0, count):
                        bsign = blocks[index].signature
                        btype = blocks[index].type
                        bx = blocks[index].x
                        by = blocks[index].y
                        bwidt = blocks[index].width
                        bheig = blocks[index].height
                        bsize = bwidt * bheig
                        angle = blocks[index].angle
                        bdist = (self.__objectHeight *
                                 self.__focalLength) / bheig
                        factor = 0
                        if (int(bsign) == int(colorCode)):
                            if((frameKey in self.__biggestBlockInFrame and self.__biggestBlockInFrame[frameKey] < bsize)
                               or ((frameKey in self.__biggestBlockInFrame) == False)):
                                self.__biggestBlockInFrame[frameKey] = bsize
                                self.__biggestBlockInFrame['color'] = int(
                                    bsign)
                                self.__biggestBlockInFrame['bx'] = int(
                                    bx)
                                self.__biggestBlockInFrame['bwidt'] = int(
                                    bwidt)
                                self.__biggestBlockInFrame['bsize'] = int(
                                    bsize)

                                if self.__biggestBlockInFrame['bx'] > 160:
                                    panDirection = 'right'
                                else:
                                    panDirection = 'left'
                                if panDirection == 'left':
                                    self.__panPosition += self.panServoRate
                                    if self.__panPosition > self.__maxPan:
                                        panDirection = 'right'
                                elif panDirection == 'right':
                                    self.__panPosition -= self.panServoRate
                                    if self.__panPosition < self.__minPan:
                                        panDirection = 'left'
                                self.__ultrasonics.ub.SetServoPosition2(
                                    self.__panPosition)

                                self.__biggestBlockInFrame['factor'] = self.__panPosition
                                if('factor' in self.__biggestBlockInFrame):
                                    factor = self.__biggestBlockInFrame['factor']
                                    if(factor > 0):
                                        # go Left
                                        if (factor > 0.33):
                                            # spin
                                            print(
                                                'spinning left @ factor:' + str(factor))
                                            self.__motors.rotate(factor * 135)
                                            self.__panPosition = 0
                                            self.__ultrasonics.ub.SetServoPosition2(
                                                self.__panPosition)
                                        else:
                                            # steer
                                            self.__motors.move(1, 0.5, 0.5)

                                    elif(self.__biggestBlockInFrame['factor'] < 0):
                                        # goright
                                        if (factor < -0.33):
                                            # spin
                                            print(
                                                'spinning Right @ factor:' + str(factor))
                                            self.__motors.rotate(factor * 135)
                                            self.__panPosition = 0
                                            self.__ultrasonics.ub.SetServoPosition2(
                                                self.__panPosition)
                                        else:
                                            # steer
                                            self.__motors.move(0.5, 1, 0.5)
                                    else:
                                        print('going straight')

                                        self.__motors.move(1, 1, 0.5)
                                else:
                                    print('going nowhere')

                                    self.__motors.move(1, 1, 0.5)
                        else:
                            self.__biggestBlockInFrame = {}
                        strOp = ('%d, %d, %d, %f, %f, %f, %f, %f, %f, %f, %f, %d, %f, %s' % (
                            frame, btype, bsign, bx, by, bwidt, bheig, bsize, angle, bdist, factor, colorCode, self.__panPosition, 'approaching'))
                        self.__logger.info(strOp)
                    frame += 1
                    time.sleep(0.01)

            except KeyboardInterrupt:
                pixy_close()
                raise
            except:
                tb = traceback.format_exc()
                e = sys.exc_info()[0]
                print(tb)
                if(self.__motors):
                    self.__motors.shutdown()
                raise

    def search(self, colorCode):
        found = False
        blocks = BlockArray(100)
        frame = 0
        print('searching')
        panDirection = 'right'

        while found == False:
            try:
                count = pixy_get_blocks(100, blocks)
                if count > 0:
                    # Blocks found #
                    frameKey = 'frame' + str(frame)
                    # print(count)

                    self.__biggestBlockInFrame = {frameKey: 0}
                    for index in range(0, count):
                        bsign = blocks[index].signature
                        btype = blocks[index].type
                        bx = blocks[index].x
                        by = blocks[index].y
                        bwidt = blocks[index].width
                        bheig = blocks[index].height
                        bsize = bwidt * bheig
                        angle = blocks[index].angle
                        bdist = (self.__objectHeight *
                                 self.__focalLength) / bheig
                        factor = 0
                        if (int(bsign) == int(colorCode)):
                            if(self.__biggestBlockInFrame[frameKey] < bsize):
                                self.__biggestBlockInFrame[frameKey] = bsize
                                self.__biggestBlockInFrame['color'] = int(
                                    bsign)
                                self.__biggestBlockInFrame['bx'] = int(
                                    bx)
                                self.__biggestBlockInFrame['bwidt'] = int(
                                    bwidt)
                                self.__biggestBlockInFrame['bsize'] = int(
                                    bsize)
                        strOp = ('%d, %d, %d, %f, %f, %f, %f, %f, %f, %f, %f, %d, %f, %s' % (
                            frame, btype, bsign, bx, by, bwidt, bheig, bsize, angle, bdist, factor, colorCode, self.__panPosition, 'searching'))

                        self.__logger.info(strOp)

                    if(self.__biggestBlockInFrame[frameKey] > self.__minSize
                       and ((self.__biggestBlockInFrame['bx'] + self.__biggestBlockInFrame['bwidt']) < 220)):
                        print("Found")
                        found = True
                        return self.__biggestBlockInFrame[frameKey]
                    else:
                        if panDirection == 'left':
                            self.__panPosition += self.panServoRate
                            if self.__panPosition > self.__maxPan:
                                panDirection = 'right'
                        elif panDirection == 'right':
                            self.__panPosition -= self.panServoRate
                            if self.__panPosition < self.__minPan:
                                panDirection = 'left'
                        self.__ultrasonics.ub.SetServoPosition2(
                            self.__panPosition)
                        found = False
                frame += 1
                time.sleep(0.01)
            except KeyboardInterrupt:

                pixy_close()

                raise
            except:
                tb = traceback.format_exc()
                e = sys.exc_info()[0]
                print(tb)
                if(self.__motors):
                    self.__motors.shutdown()
                raise
