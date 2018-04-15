#!/usr/bin/env python3
# Original Source: https://github.com/piborg/MoveMyServo

import time
import sys
import traceback

from references import UltraBorg3
from references import ThunderBorg3

from ultrasonics import Ultrasonics
from motors import Motors
from steering import Steering
from telemetry import Telemetry
from vision import Vision
from vision import VisionAttributes
from straight_line_vision import StraightLineVision
from pan_tilt_controller import PanTiltController


class Main():
    ub = UltraBorg3.UltraBorg()
    tb = ThunderBorg3.ThunderBorg()
    MODE_STRAIGHT_LINE_SPEED = 0
    MODE_OVER_THE_RAINBOW = 1
    MODE_MAZE_SOLVE = 2
    MODE_DERANGED_GOLF = 3
    MODE_DUCK_SHOOT = 4
    MODE_OBSTACLE_COURSE = 5
    MODE_PI_NOON = 6
    MODE_TEST = 99
    mode = MODE_STRAIGHT_LINE_SPEED

    def __init__(self):

        self.ub.Init()
        self.tb.Init()

        self.tickSpeed = 0.05
        self.us = Ultrasonics(self.ub)
        self.motors = Motors(self.tb, self.ub, self.tickSpeed)
        self.steering = Steering(self.tb,  self.ub, self.tickSpeed)
        self.vision = Vision(self.steering, self.motors)
        self.straight_line_speed = StraightLineVision(
            self.steering, self.motors)
        self.teleLogger = Telemetry("telemetry", "csv").get()
        self.ptc = PanTiltController(self.ub, 270, 135)

        battMin, battMax = self.tb.GetBatteryMonitoringLimits()
        battCurrent = self.tb.GetBatteryReading()
        print('Battery monitoring settings:')
        print('    Minimum  (red)     %02.2f V' % (battMin))
        print('    Half-way (yellow)  %02.2f V' % ((battMin + battMax) / 2))
        print('    Maximum  (green)   %02.2f V' % (battMax))
        print()
        print('    Current voltage    %02.2f V' % (battCurrent))
        print('    Mode %s' % (self.mode))
        print()

    def log(self):
        if (self.motors.speed != 0):
            self.teleLogger.info(
                '%(left)f, %(front)f, %(right)f, %(back)f, %(distanceMoved)f, %(forwardSpeed)f, %(direction)s, %(degree)f, %(ratio)f', {
                    "left": self.us.left,
                    "front": self.us.front,
                    "right": self.us.right,
                    "back": self.us.back,
                    "distanceMoved": self.motors.distanceMoved,
                    "forwardSpeed": self.motors.forwardSpeed,
                    "direction": self.steering.going,
                    "degree": self.steering.steeringPosition,
                    "ratio": self.steering.sideRatio
                })

    def run(self):
        try:
            if(self.mode == self.MODE_STRAIGHT_LINE_SPEED):
                print("Straight line speed")
                self.modeStraightLineSpeed()
            elif(self.mode == self.MODE_OVER_THE_RAINBOW):
                print("Rainbow")
                self.modeOverTheRainbow()
            else:

                print('Pan -62 = ' + str(self.ptc.pan(-62)))
                time.sleep(1)
                print('Pan 0 = ' + str(self.ptc.pan(0)))
                time.sleep(1)

                print('Pan 62 = ' + str(self.ptc.pan(62)))
                time.sleep(1)

                print('Pan absolute 1.0 = ' + str(self.ptc.pan_absolute(1.0)))
                time.sleep(1)

                print('Pan absolute -1.0 = ' + str(self.ptc.pan_absolute(-1.0)))
                time.sleep(1)

                print('Pan absolute 0.0 = ' + str(self.ptc.pan_absolute(0.0)))
                time.sleep(1)

                print('Tilt -30 = ' + str(self.ptc.tilt(-30)))
                time.sleep(1)
                print('Tilt 0 = ' + str(self.ptc.tilt(0)))
                time.sleep(1)

                print('Tilt 30 = ' + str(self.ptc.tilt(30)))
                time.sleep(1)

                print('Tilt absolute 0.6 = ' + str(self.ptc.tilt_absolute(0.6)))
                time.sleep(1)

                print('Tilt absolute -0.6 = ' +
                      str(self.ptc.tilt_absolute(-0.6)))
                time.sleep(1)

                print('Tilt absolute 0.0 = ' + str(self.ptc.tilt_absolute(0.0)))
                time.sleep(1)

        except KeyboardInterrupt:
            # User has pressed CTRL+C
            self.ub.SetServoPosition2(0)

            print('Done')
            if(self.motors):
                self.motors.shutdown()

        except Exception as e:
            tb = traceback.format_exc()
            e = sys.exc_info()[0]
            print(tb)
            if(self.motors):
                self.motors.shutdown()

    def modeStraightLineSpeed(self):
        self.teleLogger.info(
            'left, front, right, back, distanceMoved, forwardSpeed, direction, steering position, ratio')
        self.steering.reset()
        slVa = VisionAttributes()
        slVa.startTiltAngle = 0.6
        slVa.startPanAngle = 0
        slVa.targetMinSize = 1000
        slVa.targetMaxSize = 18000
        slVa.minPanAngle = -0.5
        slVa.maxPanAngle = 0.5
        slVa.colour = Vision.COLOUR_WHITE
        slVa.targetColorPattern = Vision.COLOUR_WHITE
        slVa.topSpeed = 0.6
        slVa.topSpinSpeed = 1.0
        self.ptc.tilt(0.5)
        slsPtc = PanTiltController(self.ub, 270, 135)
        slsPtc.initPanServo(5000, 1000)
        self.straight_line_speed.initialise(slVa, slsPtc)
        self.motors.stop()
        prev_block_position = None
        while True:
            self.straight_line_speed.track(
                self.straight_line_speed.COLOUR_WHITE)

    def modeOverTheRainbow(self):
        slVa = VisionAttributes()
        slVa.startTiltAngle = 0.12
        slVa.startPanAngle = -1.00
        slVa.targetMinSize = 25
        slVa.targetMaxSize = 2200
        slVa.minPanAngle = -1.0
        slVa.maxPanAngle = 1.0
        slVa.targetColorPattern = Vision.COLOUR_WHITE
        slVa.topSpeed = 1.0
        slVa.topSpinSpeed = 1.0

        self.motors.move(-1, -1, 0.3)
        time.sleep(0.8)
        self.motors.stop()

        rainbowPtc = PanTiltController(self.ub, 270, 135)
        rainbowPtc.initPanServo(5000, 1000)
        self.vision.initialise(slVa, rainbowPtc)
        time.sleep(0.5)

        self.vision.scan()
        print("Scan Complete")
        index = 0
        prev_position = 0

        for ball_position in self.vision.ball_positions:
            ball_position = self.vision.ball_positions[0]
            print("Size: " + str(ball_position.size) +
                  ', x :' + str(ball_position.x) +
                  ', y :' + str(ball_position.y) +
                  ', pan-position :' + str(ball_position.pan_position) +
                  ', angle : ' + str(ball_position.pan_position * 135) +
                  ', Colour:' + str(ball_position.colour))
            if (index > 0):
                prev_position = self.vision.ball_positions[index -
                                                           1].pan_position
            index = index + 1
            self.vision.goto_ball_position(ball_position, prev_position)


def main():
    controller = Main()
    controller.run()


if __name__ == '__main__':
    main()
