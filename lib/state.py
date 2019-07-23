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
        self._state = self._sm_nothing
        self._drone = Drone()


    def _sm_nothing(self):
        return self._sm_nothing


    def execute(self):
        while self._drone.is_working():
            self._state = self._state()


    def is_working(self):
        return self._drone.is_working()
        
    
    def done(self):
        self._drone.done()


if __name__ == '__main__':
    sm = StateMachine()
    sm.execute()