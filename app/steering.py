#!/usr/bin/env python3
# Original Source: https://github.com/piborg/MoveMyServo

# Import the libraries we need
from __future__ import division
import time
from references import ThunderBorg3
from datetime import datetime
from telemetry import Telemetry


class Steering():
    def __init__(self, thunderBorgInstance, ultraBorgInstance, tickSpeed):
        self.tb = thunderBorgInstance
        self.ub = ultraBorgInstance
        self.steeringPosition = 0.0
        self.logger = Telemetry(self.__class__.__name__, "log").get()

    def adjustLeft(self, factor):
        if(self.going == 'right'):
            self.steeringPosition = -1 * self.steeringDefault * factor
        elif(self.going == 'left'):
            self.steeringPosition = self.steeringPosition - \
                (self.steeringDefault * factor)
        self.going = 'left'

    def adjustRight(self, factor):
        if(self.going == 'left'):
            self.steeringPosition = (self.steeringDefault * factor)
        elif(self.going == 'right'):
            self.steeringPosition = self.steeringPosition + \
                (self.steeringDefault * factor)
        self.going = 'right'

    def steer(self, left, right, front, back):
        self.sideRatio = right / left
        if (self.sideRatio != 1):
            heading = 1 - self.sideRatio
            prevHeading = 1 - self.prevRatio
            if (self.sideRatio < 1):
                # RHS distance less than LHS distance
                # so go should go Left
                # self.adjustLeft(1)
                print("Left")
            elif (self.sideRatio > 1):
                # LHS distance less than RHS distance
                # so go Right
                # self.adjustRight(1)
                print("Right")
            else:
                self.steeringPosition = 0.0
        else:
            self.steeringPosition = 0.0

        self.prevRatio = self.sideRatio
        self.ub.SetServoPosition4(self.steeringPosition)

        if (right != 0):
            self.steer(left, right, front, back)
