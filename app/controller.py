#!/usr/bin/env python
# Original Source: https://github.com/piborg/MoveMyServo

import time
import sys
import traceback

from references import UltraBorg
from references import ThunderBorg

from ultrasonics import Ultrasonics
from motors import Motors


class Controller():
    ub = UltraBorg.UltraBorg()
    tb = ThunderBorg.ThunderBorg()

    def __init__(self):
        self.ub.Init()
        self.tb.Init()
        self.tickSpeed = .05
        self.us = Ultrasonics(self.ub)
        self.motors = Motors(self.tb, self.ub, self.tickSpeed)

    def run(self):
        try:
            while True:
                left = self.us.readLeft()
                self.motors.move(self.us.right, self.us.front,
                                 self.us.left, self.us.back)
                time.sleep(self.tickSpeed)

                right = self.us.readRight()
                self.motors.move(self.us.right, self.us.front,
                                 self.us.left, self.us.back)
                time.sleep(self.tickSpeed)

                front = self.us.readFront()
                self.motors.move(self.us.right, self.us.front,
                                 self.us.left, self.us.back)
                time.sleep(self.tickSpeed)

                back = self.us.readBack()
                self.motors.move(self.us.right, self.us.front,
                                 self.us.left, self.us.back)

                time.sleep(self.tickSpeed)
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


def main():
    controller = Controller()
    controller.run()


if __name__ == '__main__':
    main()
