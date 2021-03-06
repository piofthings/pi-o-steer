#!/usr/bin/env python3
# Original Source: https://github.com/piborg/MoveMyServo

# Import the libraries we need
from __future__ import division
import time
import math
from references import ThunderBorg3
from datetime import datetime
from telemetry import Telemetry


class Position():
    left = 0
    right = 0
    speed = 0
    timestamp = time.time()


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

    path = []
    intervalToDegreeConstant = 0.28  # seconds

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

        self.move(self.driveLeft, self.driveRight, self.speed)

    def move(self, dLeft, dRight, speed, record=False):
        pos = Position()
        if record:
            pos.left = dLeft
            pos.right = dRight
            pos.speed = speed
            pos.timestamp = time.time()
            self.path.append(pos)
        self.tb.SetMotor1(dLeft * speed)
        self.tb.SetMotor2(dRight * speed)

    def stop(self):
        self.move(0, 0, 0)

    def rotate(self, degrees, speed=1):
        t = True
        delay = ((degrees * self.intervalToDegreeConstant) / 45) / speed
        print('Rotate Degrees: ' + str(degrees) +
              ' Calculated duration: ' + str(abs(delay)))
        last_time = time.time()
        while t:
            # Go through each entry in the sequence in order
            # for step in sequence:
            if degrees < 0:
                self.tb.SetMotor1(1 * speed)
                self.tb.SetMotor2(-1 * speed)
            elif degrees > 0:
                self.tb.SetMotor1(-1 * speed)
                self.tb.SetMotor2(1 * speed)
            now = time.time()
            if (now - last_time) > abs(delay):
                t = False

        self.tb.SetMotor1(0)
        self.tb.SetMotor2(0)

        self.tb.MotorsOff()                 # Turn both motors off

    def clear_reverse_history(self):
        del self.path[:]

    def reverse(self, percent=100):
        print('Reversing! Steps: ' + str(len(self.path)))
        startIndex = len(self.path) - 1
        while startIndex > 0:
            t = True
            delay = (self.path[startIndex].timestamp -
                     self.path[startIndex - 1].timestamp)
            last_time = time.time()
            self.tb.SetMotor1(
                self.path[startIndex].right * (-1) * self.path[startIndex].speed)
            self.tb.SetMotor2(
                self.path[startIndex].left * (-1) * self.path[startIndex].speed)
            while t:
                now = time.time()
                if (now - last_time) > abs(delay):
                    t = False
                    self.tb.SetMotor1(0)
                    self.tb.SetMotor2(0)
                    del self.path[startIndex]
                    startIndex = len(self.path) - 1
            print('t = ' + str(t) + ' startIndex: ' + str(startIndex) + ' Delay: ' + str(delay) +
                  ' TimeStamp(i): ' + str(self.path[startIndex].timestamp) + ' TimeStamp(i-1): ' + str(self.path[startIndex - 1].timestamp))

    def shutdown(self):
        self.tb.MotorsOff()
        self.tb.SetCommsFailsafe(False)
        self.tb.SetLedShowBattery(False)
        self.tb.SetLeds(0, 0, 0)
