#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import cv2
import chainer

import sys
import os
import site


class FaceDetector(object):
    def __init__(self):
        xml_path = None
        
        # search dist-package
        sites = site.getsitepackages()
        for s in sites:
            tmp_path = os.path.join(s, 'cv2/data/haarcascade_frontalcatface.xml')
            if os.path.exists(tmp_path):
                xml_path = tmp_path
        
        # could not find
        if xml_path == None:
            sys.exit('Could not find haarcascade_frontalcatface.xml')

        self._cascade = cv2.CascadeClassifier(xml_path)


    def detect_face(self, frame):
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._cascade.detectMultiScale(frame_gray)

        # no face is found
        if len(faces) < 1:
            return False, None, None, None, None, None
        
        # return the biggest face
        area_max = 0
        for x, y, w, h in faces:
            if self.wh2area(w, h) <= area_max:
                continue

            area_max = self.wh2area(w, h)
            x_face = x
            y_face = y
            w_face = w
            h_face = h
            face = frame[y:y+h, x:x+w]

        return True, face, x_face, y_face, w_face, h_face


    def detect_face_chest(self, frame):
        ret, face, x_face, y_face, w_face, h_face = self.detect_face(frame)

        # no face is found
        if not ret:
            return False, None, None, None, None, None, None

        chest = frame[y_face+h_face:y_face+2*h_face, x_face:x_face+w_face]
        return True, face, chest, x_face, y_face, w_face, h_face


    def xywh2center(self, x, y, w, h):
        return x + w // 2, y + h // 2


    def wh2area(self, w, h):
        return w * h