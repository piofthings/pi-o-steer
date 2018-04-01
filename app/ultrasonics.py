#!/usr/bin/env python3

# UltraBorg library by PiBorg: https://github.com/piborg/ultraborg-web

from references import UltraBorg3
import time


class Position(object):
    def __init__(self, jsonDef):
        s = json.loads(jsonDef)
        self.left = -1 if 'left' not in s else s['left']
        self.right = -1 if 'right' not in s else s['right']
        self.front = -1 if 'front' not in s else s['front']
        self.back = -1 if 'back' not in s else s['back']


class Ultrasonics():
    __ub = None     # Create a new UltraBorg object
    left = 0.0
    right = 0.0
    front = 0.0
    back = 0.0

    def __init__(self, utraborgInstance):
        self.__ub = utraborgInstance
        self.frontPrevious = self.__ub.GetDistance2()
        # Set the board up (checks the board is connected)

    def read(self):
        # Read all four ultrasonic values
        self.right = self.__ub.GetRawDistance1()
        time.sleep(0.05)
        self.front = self.__ub.GetRawDistance2()
        time.sleep(0.05)
        self.left = self.__ub.GetRawDistance3()
        time.sleep(0.05)
        self.back = self.__ub.GetRawDistance4()
        time.sleep(0.05)
        # Convert to the nearest millimeter
        self.right = int(self.right)
        self.front = int(self.front)
        self.left = int(self.left)
        self.back = int(self.back)

    def readRight(self):
        self.right = self.__ub.GetRawDistance1()
        return self.right

    def readLeft(self):
        self.left = self.__ub.GetRawDistance3()
        return self.left

    def readFront(self):
        self.front = self.__ub.GetRawDistance2()
        return self.left

    def readBack(self):
        self.back = self.__ub.GetRawDistance4()
        return self.back
