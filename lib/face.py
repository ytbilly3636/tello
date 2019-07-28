#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import cv2

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
        
        # could not find the xml file
        if xml_path == None:
            sys.exit('Could not find haarcascade_frontalcatface.xml')

        # load xml file
        self._cascade = cv2.CascadeClassifier(xml_path)

        # for maching
        self._template = None
        self._orb = cv2.ORB_create()
        self._bfm = cv2.BFMatcher(cv2.NORM_HAMMING)


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


    def set_template(self, x, resize=(200, 200)):
        self._template = cv2.cvtColor(cv2.resize(x, resize), cv2.COLOR_BGR2GRAY)
        _, self._des_template = self._orb.detectAndCompute(self._template, None)


    def distance_template(self, x):
        if self._template is None:
            print('No template is set')
            return 0

        # feature
        img = cv2.cvtColor(cv2.resize(x, (self._template.shape[1], self._template.shape[0])), cv2.COLOR_BGR2GRAY)
        _, des = self._orb.detectAndCompute(img, None)

        # matching
        try:
            matches = self._bfm.match(des, self._des_template)
            dist = [m.distance for m in matches]

            # if python2, sys.maxint should be used instead of sys.maxsize
            return sum(dist) / (len(dist) + (1.0 / sys.maxsize))
        
        except cv2.error:
            return sys.maxsize


    def match_template(self, x, th=100):
        distance = self.distance_template(x)
        print(distance)
        ret = True if distance < th else False
        return ret

    
    def detect_template_face(self, frame):
        if self._template is None:
            print('No template is set')
            return False, None, None, None, None, None

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._cascade.detectMultiScale(frame_gray)

        # no face is found
        if len(faces) < 1:
            return False, None, None, None, None, None
        
        # return the template face
        ret = False
        face = None
        x_face = None
        y_face = None
        w_face = None
        h_face = None
        for x, y, w, h in faces:
            face = frame[y:y+h, x:x+w]

            if self.match_template(face):
                ret = True
                x_face = x
                y_face = y
                w_face = w
                h_face = h

        return ret, face, x_face, y_face, w_face, h_face