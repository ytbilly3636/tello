#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import cv2
import chainer

import sys
import os


class FaceDetector(object):
    def __init__(self, xml_path='/usr/local/lib/python3.5/dist-packages/cv2/data/haarcascade_frontalcatface_extended.xml'):
        if not os.path.exists(xml_path):
            sys.exit('Could not find xml file: ' + xml_path)

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