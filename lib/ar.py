#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import cv2
from cv2 import aruco


class ARDetector(object):
    def __init__(self, dic=aruco.DICT_4X4_50):
        # dictionary
        self._dic = aruco.getPredefinedDictionary(dic)


    def generate_marker(self, id, file_name='ar.jpg'):
        marker = aruco.drawMarker(self._dic, id, 100)
        cv2.imwrite(file_name, marker)


    def detect_marker(self, frame):
        corns, ids, _ = aruco.detectMarkers(frame, self._dic)
        return corns, ids


    def corn2center(self, corn):
        return int(min(corn[0, :, 0]) + max(corn[0, :, 0])) // 2, int(min(corn[0, :, 1]) + max(corn[0, :, 1])) // 2


    def corn2area(self, corn):
        w = int(max(corn[0, :, 0]) - min(corn[0, :, 0]))
        h = int(max(corn[0, :, 1]) - min(corn[0, :, 1]))
        return w * h