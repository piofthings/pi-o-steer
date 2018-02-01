#!/usr/bin/env python

# UltraBorg library by PiBorg: https://github.com/piborg/ultraborg-web

from references import UltraBorg
import time

class Position(object):
    def __init__(self, jsonDef):
        s = json.loads(jsonDef)
        self.left = -1 if 'left' not in s else s['left']
        self.right = -1 if 'right' not in s else s['right']
        self.front = -1 if 'front' not in s else s['front']
        self.back = -1 if 'back' not in s else s['back']

class Ultrasonics():
    ub = None     # Create a new UltraBorg object

    def __init__(self, utraborgInstance):
        self.ub = utraborgInstance
        self.frontPrevious = self.ub.GetDistance2()
        # Set the board up (checks the board is connected)

    def read(self):
        # Read all four ultrasonic values
        self.right = self.ub.GetDistance1()
        time.sleep(0.05)
        self.front = self.ub.GetDistance2()
        time.sleep(0.05)
        self.left = self.ub.GetDistance3()
        time.sleep(0.05)
        self.back = self.ub.GetDistance4()
        time.sleep(0.05)
        # Convert to the nearest millimeter
        self.right = int(self.right)
        self.front = int(self.front)
        self.left = int(self.left)
        self.back = int(self.back)
        # Display the readings
        #if self.right == 0:
            #print '#1 (Right) No reading'
        #else:
            #print '#1 (Right) % 4d mm' % (self.right)
        # if self.front == 0:
        #     print '#2 (Front) No reading'
        # else:
        #     print '#2 (Front) % 4d mm' % (self.front)
        #if self.left == 0:
            #print '#3 (Left) No reading'
        #else:
            #print '#3 (Left)  % 4d mm' % (self.left)
        #if self.back == 0:
            #print '#4 (Back) No reading'
        #else:
            #print '#4 (Back)  % 4d mm' % (self.back)
        #print
