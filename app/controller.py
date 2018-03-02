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


class Controller():
    ub = UltraBorg3.UltraBorg()
    tb = ThunderBorg3.ThunderBorg()
    MODE_STRAIGHT_LINE_SPEED = 0
    MODE_OVER_THE_RAINBOW = 1
    MODE_MAZE_SOLVE = 2
    MODE_DERANGED_GOLF = 3
    MODE_DUCK_SHOOT = 4
    MODE_OBSTACLE_COURSE = 5
    MODE_PI_NOON = 6

    def __init__(self):
        self.ub.Init()
        self.tb.Init()
        self.tickSpeed = 0.05
        self.us = Ultrasonics(self.ub)
        self.motors = Motors(self.tb, self.ub, self.tickSpeed)
        self.steering = Steering(self.tb,  self.ub, self.tickSpeed)
        self.vision = Vision(self.steering, self.us)
        self.teleLogger = Telemetry("telemetry", "csv").get()
        self.mode = self.MODE_OVER_THE_RAINBOW

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
                self.modeStraightLineSpeed()
            elif(self.mode == self.MODE_OVER_THE_RAINBOW):
                self.vision.watch()
                print("Ball ball ball ball ball")
                # front = self.us.readFront()
                # self.motors.move(self.us.right, self.us.front,
                #                  self.us.left, self.us.back)
                # time.sleep(self.tickSpeed)

                # back = self.us.readBack()
                # self.motors.move(self.us.right, self.us.front,
                #                  self.us.left, self.us.back)
                # time.sleep(self.tickSpeed)
        except KeyboardInterrupt:
            # User has pressed CTRL+C
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
        while True:
            left = self.us.readLeft()
            self.steering.steer(self.us.left, self.us.right,
                                self.us.front, self.us.back)
            self.motors.move(self.us.left, self.us.right,
                             self.us.front, self.us.back)
            self.log()
            time.sleep(self.tickSpeed)

            right = self.us.readRight()
            self.steering.steer(self.us.left, self.us.right,
                                self.us.front, self.us.back)
            self.motors.move(self.us.left, self.us.right,
                             self.us.front, self.us.back)
            self.log()
            time.sleep(self.tickSpeed)


def main():
    controller = Controller()
    controller.run()


if __name__ == '__main__':
    main()
