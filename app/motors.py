#!/usr/bin/env python3
# Original Source: https://github.com/piborg/MoveMyServo

# Import the libraries we need
from __future__ import division
import time
from references import ThunderBorg3
from datetime import datetime
from telemetry import Telemetry


class Motors():
    tickSpeed = 0.1  # seconds
    forwardSpeed = 0.0
    leftSpeed = 0.0
    rightSpeed = 0.0
    reverseSpeed = 0.0
    steeringMin = -0.90                 # Smallest servo position to use
    steeringMax = +0.90
    frontPrev = 0
    left = 1
    right = 1
    prevRight = -1
    sideRatio = 1.0
    prevRatio = 1.0
    going = 'straight'
    minRight = 80
    steeringDefault = 0.08
    distanceMoved = 0

    def __init__(self, thunderBorgInstance, ultraBorgInstance, tickSpeed):
        self.tb = thunderBorgInstance
        self.ub = ultraBorgInstance
        self.tickSpeed = tickSpeed
        self.safeDistance = 500  # mm
        self.steeringPosition = 0.0
        self.logger = Telemetry(self.__class__.__name__, "log").get()

        self.ub.SetServoPosition4(self.steeringPosition)

        if not self.tb.foundChip:
            boards = ThunderBorg.ScanForThunderBorg()
            if len(boards) == 0:
                self.logger.info(
                    'No ThunderBorg found, check you are attached :)')
            else:
                self.logger.info("No ThunderBorg at address %02X, but we did find boards:" % (
                    self.tb.i2cAddress))
                for board in boards:
                    print(' %02X (%d)' % (board, board))
                self.logger.info(
                    'If you need to change the I2C address change the setup line so it is correct, e.g.')
                self.logger.info('self.tb.i2cAddress = 0x%02X' % (boards[0]))
            sys.exit()
        # Ensure the communications failsafe has been enabled!
        failsafe = False
        for i in range(5):
            self.tb.SetCommsFailsafe(True)
            failsafe = self.tb.GetCommsFailsafe()
            if failsafe:
                break
        if not failsafe:
            self.logger.info('Board %02X failed to report in failsafe mode!' %
                             (self.tb.i2cAddress))
            sys.exit()

        self.driveRight = 1.0
        self.driveLeft = 1.0
        # Power settings
        # Total battery voltage to the ThunderBorg
        self.voltageIn = 3.7 * 4
        # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power
        self.voltageOut = self.voltageIn * 0.95

        # Setup the power limits
        if self.voltageOut > self.voltageIn:
            self.maxPower = 0.5
        else:
            self.maxPower = self.voltageOut / float(self.voltageIn)

        self.speed = self.maxPower

        self.tb.MotorsOff()
        self.center()

    def center(self):
        self.ub.SetServoPosition4(0)

    def move(self, left, right, front, back):
        distanceMoved = -1
        if (front != 'No reading'):
            if (self.frontPrev != 0):
                distanceMoved = (self.frontPrev - front)

                if (distanceMoved > 0 and self.speed > 0):
                    self.forwardSpeed = (
                        self.frontPrev - front) / self.tickSpeed  # mm/seconds

                if (self.forwardSpeed > front and front < 20):
                    self.speed = self.speed / 2
                else:
                    if (front < distanceMoved * 1.5 or front < 200):
                        self.speed = 0
            self.frontPrev = front
        else:
            self.logger.info('Distance moved was not read')

        self.tb.SetMotor1(self.driveRight * self.speed)
        self.tb.SetMotor2(self.driveLeft * self.speed)

    def shutdown(self):
        self.tb.MotorsOff()
        self.tb.SetCommsFailsafe(False)
        self.tb.SetLedShowBattery(False)
        self.tb.SetLeds(0, 0, 0)
