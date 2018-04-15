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


class Blocks (Structure):
    _fields_ = [("type", c_uint),
                ("signature", c_uint),
                ("x", c_uint),
                ("y", c_uint),
                ("width", c_uint),
                ("height", c_uint),
                ("angle", c_uint)]


class VisionAttributes():
    startPanAngle = 0
    startTiltAngle = 0
    targetMinSize = 100
    targetMaxSize = 500
    minPanAngle = -0.5  # -1.0 to +1.0
    maxPanAngle = 0.5  # -1.0 to +1.0
    minTiltAngle = -0.5  # -1.0 to +1.0
    maxTiltAngle = 0.5  # -1.0 to +1.0
    targetColorPattern = "1"
    topSpeed = 1.0
    topSpinSpeed = 1.0

    def __init__(self):
        self.startTiltAngle = 0


class BlockPosition():
    colour = -99
    x = -1
    y = -1
    width = 0
    height = 0
    size = 0
    angle = 360
    pan_position = 360
    frame_key = 'unknown'
    factor = 0
    centered = False

    def __init__(self, colour=-99, framekey='unknown'):
        self.colour = colour
        self.frame_key = framekey


class Vision():
    """Vision class to handle PixyCam Data"""
    COLOUR_WHITE = 7  # White
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

    ball_positions = [BlockPosition(COLOUR_RED), BlockPosition(COLOUR_BLUE),
                      BlockPosition(COLOUR_YELLOW), BlockPosition(COLOUR_GREEN)]

    __biggest_block_in_frame = dict()

    def __init__(self, steering, motors):
        super(Vision, self).__init__()
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
        self.__pan_tilt_controller = ptc
        self.__pan_tilt_controller.pan_absolute(0)
        self.__pan_tilt_controller.tilt_absolute(
            0)

    def scan(self):
        print("self.__pan_position = " + str(self.__pan_position))
        str(self.__pan_tilt_controller.pan_absolute(self.__pan_position))
        str(self.__pan_tilt_controller.tilt_absolute(self.__tilt_position))
        time.sleep(0.5)
        not_in_view = True
        first_colour_found = False
        colour_code = self.COLOUR_UNKNOWN
        colours_found = False
        blocks = BlockArray(100)
        frame = 0
        strOp = ""
        factor = False
        while colours_found != True:

            try:
                count = pixy_get_blocks(100, blocks)
                if count > 0:
                    first_colour_found = True
                    frameKey = 'frame' + str(frame)

                    self.__biggest_block_in_frame = BlockPosition(
                        self.COLOUR_UNKNOWN, frameKey)
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
                        if(self.__biggest_block_in_frame.size < bsize):
                            self.__biggest_block_in_frame.size = bsize
                            self.__biggest_block_in_frame.colour = int(
                                bsign)
                            self.__biggest_block_in_frame.x = int(
                                bx)
                            self.__biggest_block_in_frame.y = int(
                                by)
                            self.__biggest_block_in_frame.width = int(
                                bwidt)
                            self.__biggest_block_in_frame.size = int(
                                bsize)
                            self.__biggest_block_in_frame.pan_position = self.__pan_position

                    factor = self.__update_if_better_block_position(
                        self.__biggest_block_in_frame)

                    strOp = ('%d, %d, %d, %f, %f, %f, %f, %f, %f, %f, %s, %d, %f, %s' % (
                        frame, btype, bsign, bx, by, bwidt, bheig, bsize, angle, bdist, str(factor), colour_code, self.__pan_position, 'scanning'))

                self.__pan_position = self.__pan_position + \
                    self.__pan_tilt_controller.abs_pan_per_degree

                self.__pan_tilt_controller.pan_absolute(self.__pan_position)
                if strOp != "":
                    self.__logger.info(strOp)
                frame += 1
                time.sleep(0.02)
                colours_found = self.__all_colours_found(
                ) and self.__pan_position > (self.__visionAttributes.maxPanAngle) * 0.95

            except KeyboardInterrupt:
                pixy_close()
                print("Closed Pixy")
                raise

            except:
                tb = traceback.format_exc()
                e = sys.exc_info()[0]
                print(tb)
                if(self.__motors):
                    self.__motors.shutdown()
                raise

    def __update_if_better_block_position(self, current_block_position):
        if((current_block_position.size > self.__visionAttributes.targetMinSize)
           and ((current_block_position.x + current_block_position.width) < 220)
           and ((current_block_position.y > 15))
           and ((current_block_position.y < 140))):

            ball_position = self.__get_ball_position_of_colour(
                current_block_position.colour)

            x_distance_from_center = abs(
                self.ball_positions[ball_position].x - self.PIXY_RES_X / 2)
            new_x_distance_from_center = abs(
                current_block_position.x - self.PIXY_RES_X / 2)
            if(new_x_distance_from_center < x_distance_from_center):

                self.ball_positions[ball_position] = current_block_position
                return True
            else:
                return False
        else:
            return False

    def __get_ball_position_of_colour(self, colour):
        index = 0
        for ball_position in self.ball_positions:
            if ball_position.colour == colour:
                return index
            else:
                index = index + 1
        return -1

    def __all_colours_found(self):

        for ball_position in self.ball_positions:
            if ball_position.pan_position == 360:
                return False
        return True

    def goto_ball_position(self, ball_position, previous_position=0):
        reached = False
        self.__pan_position = 0
        self.__pan_tilt_controller.pan(self.__pan_position)
        turn_by = (ball_position.pan_position - previous_position) * -135
        self.__motors.rotate(turn_by, 0.5)
        # self.__pan_tilt_controller.tilt(-0.05)
        self.__pan_position = 0
        self.__pan_tilt_controller.pan(self.__pan_position)
        while reached == False:
            tracked = False
            current_block_position = self.track(ball_position.colour)
            tracked = current_block_position != None
            if tracked:
                current_block_position.factor = current_block_position.pan_position
                # if(current_block_position.y < current_block_position.height / 2):
                #     while (current_block_position.y < current_block_position.height / 2):
                #         self.__pan_tilt_controller.tilt(
                #             self.__pan_tilt_controller.current_tilt - self.__pan_tilt_controller.abs_tilt_per_degree)
                self.drive_to(current_block_position,
                              current_block_position.colour)
                print("Size: " + str(current_block_position.size))
                reached = current_block_position.size >= self.__visionAttributes.targetMaxSize
            else:
                self.__motors.stop()

        self.__steering.steerAbsolute(0)
        self.__motors.reverse()
        self.__motors.clear_reverse_history()

    def track(self, colour_code):
        centered = False
        blocks = BlockArray(100)
        pan_dir = 'left'

        current_block_position = BlockPosition()
        frame = -1
        while centered == False:
            frame = frame + 1
            count = pixy_get_blocks(100, blocks)
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
                        if current_block_position.x > 160:
                            pan_dir = 'right'
                        else:
                            pan_dir = 'left'
                        if((current_block_position.size > self.__visionAttributes.targetMinSize)
                           and (current_block_position.x < ((self.PIXY_RES_X / 2) - (current_block_position.width / 2)))
                           and (current_block_position.x > (self.PIXY_RES_X / 2) - (current_block_position.width))
                           # and ((current_block_position.y > 15))
                           # and ((current_block_position.y < 140))
                           ):
                            self.__pan_tilt_controller.pan_absolute(
                                self.__pan_position)
                            self.__steering.steerAbsolute(
                                self.__pan_position * 2)
                            current_block_position.pan_position = self.__pan_position
                            strOp = ('%d, %d, %d, %f, %f, %f, %f, %f, %f, %f, %s, %d, %f, %s' % (
                                frame, btype, current_block_position.colour, current_block_position.x, current_block_position.y, current_block_position.width, current_block_position.height, current_block_position.size, angle, bdist, "Found Colour & Size", colour_code, self.__pan_position, 'tracking'))
                            self.__logger.info(strOp)
                            centered = True
                        else:
                            strOp = ('%d, %d, %d, %f, %f, %f, %f, %f, %f, %f, %s, %d, %f, %s' % (
                                frame, btype, current_block_position.colour, current_block_position.x, current_block_position.y, current_block_position.width, current_block_position.height, current_block_position.size, angle, bdist, "Size Not Matched", colour_code, self.__pan_position, 'tracking'))
                            self.__logger.info(strOp)
                    else:
                        strOp = ('%d, %d, %d, %f, %f, %f, %f, %f, %f, %f, %s, %d, %f, %s' % (
                            frame, btype, current_block_position.colour, current_block_position.x, current_block_position.y, current_block_position.width, current_block_position.height, current_block_position.size, angle, bdist, "Colour Not Matched", colour_code, self.__pan_position, 'tracking'))
                        self.__logger.info(strOp)

                if centered == False:
                    print("Centered == False && count > 0")
                    pan_dir = self.__pan(pan_dir)
                    time.sleep(0.01)

            else:
                print("Centered == False && count == 0")

                pan_dir = self.__pan(pan_dir)
                time.sleep(0.01)

        return current_block_position

    def __pan(self, pan_dir):
        if pan_dir == 'left':
            self.__pan_position = self.__pan_position + \
                self.__pan_tilt_controller.abs_pan_per_degree
            if self.__pan_position > self.__visionAttributes.maxPanAngle:
                pan_dir = 'right'

        elif pan_dir == 'right':
            self.__pan_position = self.__pan_position - \
                self.__pan_tilt_controller.abs_pan_per_degree

            if self.__pan_position < self.__visionAttributes.minPanAngle:
                pan_dir = 'left'
        if (self.__pan_position < self.__visionAttributes.maxPanAngle) and (self.__pan_position > self.__visionAttributes.minPanAngle):
            self.__pan_tilt_controller.pan_absolute(
                self.__pan_position)
            self.__steering.steerAbsolute(
                self.__pan_position * -2)

            print('__pan_position applied to ' +
                  str(self.__pan_position))
        return pan_dir

    def drive_to(self, current_block_position, colour_code):
        print("Driving to:  " + str(current_block_position.pan_position) +
              " : " + str(current_block_position.colour))
        self.__steering.steerAbsolute(current_block_position.pan_position * -2)
        self.__motors.move(1, 1, 0.3, True)
        time.sleep(0.02)
        # self.track(current_block_position.colour)

    # def approach(self, current_block_position, colour_code):
    #     reached = False
    #     blocks = BlockArray(100)
    #     frame = 0
    #     while reached == False:
    #         try:
    #             if('colour' in self.__biggest_block_in_frame):
    #                 if (self.__biggest_block_in_frame['colour'] == colour_code):
    #                     # print('colour match')
    #
    #                     if(self.__biggest_block_in_frame['bsize'] > self.__visionAttributes.targetMinSize
    #                        and self.__biggest_block_in_frame['bsize'] < self.__visionAttributes.targetMaxSize):
    #                         self.__steering.steerAbsolute(0)
    #                     else:
    #                         self.__motors.move(1, 1, 0)
    #
    #                     if(self.__biggest_block_in_frame['bsize'] >= self.__visionAttributes.targetMaxSize):
    #                         self.__motors.move(1, 1, 0)
    #
    #                         reached = True
    #                     else:
    #
    #                         reached = False
    #                 else:
    #                     self.__motors.move(1, 1, 0)
    #             else:
    #                 self.__motors.move(1, 1, 0)
    #
    #             count = pixy_get_blocks(100, blocks)
    #             if count > 0:
    #
    #                 # Blocks found #
    #                 frameKey = 'frame' + str(frame)
    #
    #                 # self.__biggest_block_in_frame = {frameKey: 0}
    #                 for index in range(0, count):
    #                     bsign = blocks[index].signature
    #                     btype = blocks[index].type
    #                     bx = blocks[index].x
    #                     by = blocks[index].y
    #                     bwidt = blocks[index].width
    #                     bheig = blocks[index].height
    #                     bsize = bwidt * bheig
    #                     angle = blocks[index].angle
    #                     bdist = (self.__objectHeight *
    #                              self.__focalLength) / bheig
    #                     factor = 0
    #                     if (int(bsign) == int(colour_code)):
    #                         if((frameKey in self.__biggest_block_in_frame and self.__biggest_block_in_frame[frameKey] < bsize)
    #                            or ((frameKey in self.__biggest_block_in_frame) == False)):
    #                             self.__biggest_block_in_frame[frameKey] = bsize
    #                             self.__biggest_block_in_frame['colour'] = int(
    #                                 bsign)
    #                             self.__biggest_block_in_frame['bx'] = int(
    #                                 bx)
    #                             self.__biggest_block_in_frame['bwidt'] = int(
    #                                 bwidt)
    #                             self.__biggest_block_in_frame['bsize'] = int(
    #                                 bsize)
    #
    #                             if self.__biggest_block_in_frame['bx'] > 160:
    #                                 panDirection = 'right'
    #                             else:
    #                                 panDirection = 'left'
    #                             if panDirection == 'left':
    #                                 self.__pan_position += self.__pan_tilt_controller.abs_pan_per_degree
    #                                 if self.__pan_position > self.__visionAttributes.maxPanAngle:
    #                                     panDirection = 'right'
    #                             elif panDirection == 'right':
    #                                 self.__pan_position -= self.__pan_tilt_controller.abs_pan_per_degree
    #                                 if self.__pan_position < self.__visionAttributes.minPanAngle:
    #                                     panDirection = 'left'
    #                             self.__pan_tilt_controller.pan_absolute(
    #                                 self.__pan_position)
    #
    #                             self.__biggest_block_in_frame['factor'] = self.__pan_position
    #                             if('factor' in self.__biggest_block_in_frame):
    #                                 factor = self.__biggest_block_in_frame['factor']
    #                                 if(factor > 0):
    #                                     # go Left
    #                                     if (factor > 0.33):
    #                                         # spin
    #                                         print(
    #                                             'spinning left @ factor:' + str(factor))
    #                                         self.__motors.rotate(
    #                                             factor * 135 * -1)
    #                                         self.__pan_position = 0
    #                                         self.__pan_tilt_controller.pan_absolute(
    #                                             self.__pan_position)
    #                                     else:
    #                                         # steer
    #                                         factor = factor / -1
    #                                         self.__steering.steerAbsolute(
    #                                             factor)
    #                                         self.__motors.move(1, 1, 1)
    #
    #                                 elif(self.__biggest_block_in_frame['factor'] < 0):
    #                                     # goright
    #                                     if (factor < -0.33):
    #                                         # spin
    #                                         print(
    #                                             'spinning Right @ factor:' + str(factor))
    #                                         self.__motors.rotate(
    #                                             factor * 135 * -1)
    #                                         self.__pan_position = 0
    #                                         self.__pan_tilt_controller.pan_absolute(
    #                                             self.__pan_position)
    #                                     else:
    #                                         # steer
    #                                         factor = factor / -1
    #                                         self.__steering.steerAbsolute(
    #                                             factor)
    #                                         self.__motors.move(1, 1, 1)
    #                                 else:
    #                                     print('going straight')
    #                                     factor = 0
    #                                     self.__steering.steerAbsolute(factor)
    #                                     self.__motors.move(1, 1, 1)
    #                             else:
    #                                 print('going nowhere')
    #
    #                                 self.__motors.move(1, 1, 1)
    #                     else:
    #                         self.__biggest_block_in_frame = {}
    #                     strOp = ('%d, %d, %d, %f, %f, %f, %f, %f, %f, %f, %f, %d, %f, %s' % (
    #                         frame, btype, bsign, bx, by, bwidt, bheig, bsize, angle, bdist, factor, colour_code, self.__pan_position, 'approaching'))
    #                     self.__logger.info(strOp)
    #                 frame += 1
    #                 time.sleep(0.02)
    #
    #         except KeyboardInterrupt:
    #             self.dispose()
    #             raise
    #         except:
    #             self.dispose()
    #
    #             tb = traceback.format_exc()
    #             e = sys.exc_info()[0]
    #             print(tb)
    #             if(self.__motors):
    #                 self.__motors.shutdown()
    #             raise
    #
    # def search(self, colour_code):
    #     found = False
    #     blocks = BlockArray(100)
    #     frame = 0
    #     panDirection = 'right'
    #
    #     while found == False:
    #         try:
    #             count = pixy_get_blocks(100, blocks)
    #             if count > 0:
    #                 # print('count > 0')
    #                 # Blocks found #
    #                 frameKey = 'frame' + str(frame)
    #                 # print(count)
    #
    #                 self.__biggest_block_in_frame = {frameKey: 0}
    #                 for index in range(0, count):
    #                     bsign = blocks[index].signature
    #                     btype = blocks[index].type
    #                     bx = blocks[index].x
    #                     by = blocks[index].y
    #                     bwidt = blocks[index].width
    #                     bheig = blocks[index].height
    #                     bsize = bwidt * bheig
    #                     angle = blocks[index].angle
    #                     bdist = (self.__objectHeight *
    #                              self.__focalLength) / bheig
    #                     factor = 0
    #                     if (int(bsign) == int(colour_code)):
    #                         if(self.__biggest_block_in_frame[frameKey] < bsize):
    #                             self.__biggest_block_in_frame[frameKey] = bsize
    #                             self.__biggest_block_in_frame['colour'] = int(
    #                                 bsign)
    #                             self.__biggest_block_in_frame['bx'] = int(
    #                                 bx)
    #                             self.__biggest_block_in_frame['bwidt'] = int(
    #                                 bwidt)
    #                             self.__biggest_block_in_frame['bsize'] = int(
    #                                 bsize)
    #
    #                 if(self.__biggest_block_in_frame[frameKey] > self.__visionAttributes.targetMinSize
    #                    and ((self.__biggest_block_in_frame['bx'] + self.__biggest_block_in_frame['bwidt']) < 220)):
    #                     found = True
    #                     return self.__biggest_block_in_frame[frameKey]
    #                 else:
    #                     if panDirection == 'left':
    #                         self.__pan_position += self.__pan_tilt_controller.abs_pan_per_degree
    #                         if self.__pan_position > self.__visionAttributes.maxPanAngle:
    #                             panDirection = 'right'
    #                     elif panDirection == 'right':
    #                         self.__pan_position -= self.__pan_tilt_controller.abs_pan_per_degree
    #                         if self.__pan_position < self.__visionAttributes.minPanAngle:
    #                             panDirection = 'left'
    #                     self.__pan_tilt_controller.pan_absolute(
    #                         self.__pan_position)
    #                     found = False
    #
    #                 strOp = ('%d, %d, %d, %f, %f, %f, %f, %f, %f, %f, %f, %d, %f, %s' % (
    #                     frame, btype, bsign, bx, by, bwidt, bheig, bsize, angle, bdist, factor, colour_code, self.__pan_position, 'searching'))
    #
    #             else:
    #                 strOp = ""
    #
    #             if strOp != "":
    #                 self.__logger.info(strOp)
    #             frame += 1
    #             time.sleep(0.01)
    #         except KeyboardInterrupt:
    #
    #             pixy_close()
    #
    #             raise
    #         except:
    #             tb = traceback.format_exc()
    #             e = sys.exc_info()[0]
    #             print(tb)
    #             if(self.__motors):
    #                 self.__motors.shutdown()
    #             raise

    def dispose(self):
        pixy_close()
