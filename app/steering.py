#!/usr/bin/env python3
# Original Source: https://github.com/piborg/MoveMyServo

# Import the libraries we need
from __future__ import division
import time
import math
from datetime import datetime
from telemetry import Telemetry


class Steering():
    __prevRatio = 0
    __prevLeft = 0
    __prevRight = 0
    __left = 0
    __right = 0
    __minRight = 150
    __minLeft = 150
    __queue = []
    steeringDefault = 0
    __servoMin = -0.90                 # Smallest servo position to use
    __servoMax = +0.90

    def __init__(self, thunderBorgInstance, ultraBorgInstance, tickSpeed):
        self.tb = thunderBorgInstance
        self.ub = ultraBorgInstance
        self.logger = Telemetry(self.__class__.__name__, "log").get()
        self.going = 'straight'
        self.__defaultTurnRatio = 0.16
        self.steeringPosition = 0

    def __adjustLeft(self, factor):
        self.steeringPosition = -1 * self.__defaultTurnRatio * factor
        self.going = 'left'

    def __adjustRight(self, factor):
        self.steeringPosition = (self.__defaultTurnRatio * factor)
        self.going = 'right'

    def reset(self):
        self.steeringPosition = self.steeringDefault
        self.ub.SetServoPosition4(self.steeringPosition)

    def steerRight(self, factor):
        self.__adjustRight(factor)
        self.ub.SetServoPosition4(self.steeringPosition)

    def steerLeft(self, factor):
        self.__adjustLeft(factor)
        self.ub.SetServoPosition4(self.steeringPosition)

    def steerAbsolute(self, value):
        if (value >= self.__servoMin and value <= self.__servoMax):
            self.steeringPosition = value
            self.ub.SetServoPosition4(self.steeringPosition)

    def steer(self, left, right, front, back):
        if(left < self.__minLeft):
            left = self.__minLeft
        if(right < self.__minRight):
            right = self.__minRight
        try:
            factor = math.log(abs(right - left), 10)
        except Exception as e:
            factor = 0

        self.sideRatio = right / left
        if ((self.sideRatio != 1)):
            if (left > right):  # and (abs(self.__prevLeft - left) > 0.5):
                # RHS distance less than LHS distance
                # so should go Left
                self.going = 'left'
                self.__adjustLeft(factor)
                self.__prevLeft = left
                self.__prevRight = right
            elif (right > left):  # and (abs(self.__prevLeft - left) > 0.5)):
                # LHS distance less than RHS distance
                # so go Right
                self.going = 'right'
                self.__adjustRight(factor)
                self.__prevLeft = left
                self.__prevRight = right
            else:
                self.going = 'straight'
                self.steeringPosition = 0.0
        else:
            self.going = 'straight'
            self.steeringPosition = 0.0

        self.__prevRatio = self.sideRatio

        self.ub.SetServoPosition4(self.steeringPosition)

        # if (right != 0):
        #     self.steer(left, right, front, back)
