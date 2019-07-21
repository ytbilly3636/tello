#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../tello'))
from lib.drone import Drone

import numpy as np
import cv2


class StateMachine(object):
    def __init__(self):
        self._state = self._do_nothing
        self._drone = Drone()


    def _do_nothing(self):
        return self._do_nothing


    def execute(self):
        while True:
            # state transition
            self._state = self._state()

            # camera
            ret, img = self._drone.get_camera()
            if not ret:
                img = np.zeros((480, 640), np.uint8)

            cv2.imshow('window', img)
            key = cv2.waitKey(1)

            # forced termination
            if key & 0xFF == ord('q'):
                break

        self._drone.land()
        cv2.destroyAllWindows()
        cv2.waitKey(1)


if __name__ == '__main__':
    sm = StateMachine()
    sm.execute()