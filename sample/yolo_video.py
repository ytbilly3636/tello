#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../tello'))
from lib import StateMachine, YOLO

import cv2
import time


class YOLOVideo(StateMachine):
    def __init__(self):
        super(YOLOVideo, self).__init__()
        self._state = self._sm_video
        self._yolo = YOLO()


    def _sm_video(self):
        while self.is_working():
            # get camera image
            ret, img = self._drone.subscribe_frame()
            if not ret:
                continue

            # detection
            b, c, i = self._yolo.detect(img)
            img = self._yolo.draw_boxes(img, b, i)

            # publish image
            self._drone.publish_frame(img)


if __name__ == '__main__':
    yolo = YOLOVideo()
    yolo.execute()