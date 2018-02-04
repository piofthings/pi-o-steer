#!/usr/bin/env python
# Original Source: https://github.com/piborg/MoveMyServo

# Import the libraries we need
from __future__ import division
from references import ThunderBorg
from datetime import datetime
import time

class Motors():
    tickSpeed = 0.1 #seconds
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
    sideRatio = 0.0
    prevRatio = -1.0
    going = 'straight'
    minRight = 80

    def __init__(self, thunderBorgInstance, ultraBorgInstance, tickSpeed):
        self.tb = thunderBorgInstance
        self.ub = ultraBorgInstance
        self.tickSpeed = tickSpeed
        self.safeDistance = 500 #mm
        self.steeringPosition = 0.0

        self.ub.SetServoPosition4(self.steeringPosition)
        if not self.tb.foundChip:
            boards = ThunderBorg.ScanForThunderBorg()
            if len(boards) == 0:
                print ('No ThunderBorg found, check you are attached :)')
            else:
                print ("No ThunderBorg at address %02X, but we did find boards:" % (self.tb.i2cAddress))
                for board in boards:
                    print ' %02X (%d)' % (board, board)
                print ('If you need to change the I2C address change the setup line so it is correct, e.g.')
                print ('self.tb.i2cAddress = 0x%02X' % (boards[0]))
            sys.exit()
        # Ensure the communications failsafe has been enabled!
        failsafe = False
        for i in range(5):
            self.tb.SetCommsFailsafe(True)
            failsafe = self.tb.GetCommsFailsafe()
            if failsafe:
                break
        if not failsafe:
            print ('Board %02X failed to report in failsafe mode!' % (self.tb.i2cAddress))
            sys.exit()

        self.driveRight = 1.0
        self.driveLeft = 1.0
        # Power settings
        self.voltageIn = 1.2 * 10                    # Total battery voltage to the ThunderBorg
        self.voltageOut = 12.0 * 0.95                # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power


        # Setup the power limits
        if self.voltageOut > self.voltageIn:
            self.maxPower = 0.5
        else:
            self.maxPower = self.voltageOut / float(self.voltageIn)

        self.speed = 0.8 #self.maxPower;

        self.tb.MotorsOff()



    def move(self, right, front, left, back):
        distanceMoved = -1
        if (front != 'No reading'):
            if (self.frontPrev != 0):
                distanceMoved = (self.frontPrev - front)

                if (distanceMoved > 0 and self.speed > 0):
                    self.forwardSpeed = (self.frontPrev - front)/self.tickSpeed #mm/seconds

                if (self.forwardSpeed > front and front < 20):
                    self.speed = self.speed/2
                else:
                    if (front < distanceMoved * 1.5 or front < 200):
                        self.speed = 0
            self.frontPrev = front
        else:
            print 'Distance moved was not read'

        if (right != 0):
            self.steer(left, right, front, back)

        self.tb.SetMotor1(self.driveRight * self.speed)
        self.tb.SetMotor2(self.driveLeft * self.speed)

        if (self.speed != 0):
            print ('Distance moved %d' % distanceMoved)
            print ('Left  % 4d mm' % (left))
            print ('Front %(front) 4d mm and speed %(forwardSpeed) 4d  mm/s' % { "front": front, "forwardSpeed": self.forwardSpeed })
            print ('Right % 4d mm' % (right))
            print ('Going %(direction) s Steering %(degree) f deg Ratio %(ratio) f' % { "direction": self.going, "degree" : self.steeringPosition, "ratio": self.sideRatio })
            print (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            print ('----------------------------------')
#        print 'Back  % 4d mm' % (back)
        #self.lef

    def steer (self, left, right, front, back):
        if(self.prevRight == -1):
            self.prevRight = right/left
            self.prevRatio = 1
        else :
            print (self.prevRight)
            print (right)
            self.sideRatio =  right/left;
            if (self.sideRatio < self.prevRatio): #left more than right go left
                self.going = 'right'
                if self.steeringPosition > 0 :
                    self.steeringPosition = -0.08
                else:
                    self.steeringPosition = self.steeringPosition - 0.08
            elif (self.sideRatio > self.prevRatio): #right more than left go right
                self.going = 'left'
                if self.steeringPosition < 0 :
                    self.steeringPosition = 0.08
                else:
                    self.steeringPosition = self.steeringPosition + 0.08
            else:
                self.steeringPosition = 0.0

            self.prevRatio = self.sideRatio

            self.ub.SetServoPosition4(self.steeringPosition)
            #self.prevRatio = self.prevRatio

    def shutdown(self):
        self.tb.MotorsOff()
        self.tb.SetCommsFailsafe(False)
        self.tb.SetLedShowBattery(False)
        self.tb.SetLeds(0,0,0)
