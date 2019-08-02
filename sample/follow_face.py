#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../tello'))
from lib import StateMachine, FaceDetector

import cv2
import time


class Follow(StateMachine):
    def __init__(self, 
        area_target = 20000, 
        area_th     = 5000, 
        center_th   = 100,
        tg          = 0.2,
        vx          = 0.15,
        vr          = 0.4,
        vz          = 0.4,
        dbg         = False
        ):
        super(Follow, self).__init__()
        self._state = self._sm_takeoff

        self._face = FaceDetector()

        # hyperparameters
        self._area_target = area_target
        self._area_th = area_th
        self._center_th = center_th
        self._tg = tg
        self._vx = vx
        self._vr = vr
        self._vz = vz

        # debug mode
        self._debug = dbg


    def _sm_takeoff(self):
        print('********** take off **********')
        if not self._debug:
            self._drone.takeoff()
            time.sleep(3)
        return self._sm_goup


    def _sm_goup(self):
        print('********** go up **********')
        if not self._debug:
            self._drone.controll(t=1.0, vz=0.5)
        return self._sm_remember_person


    def _sm_remember_person(self):
        while self.is_working():
            # get camera image
            ret, img = self._drone.subscribe_frame()
            if not ret:
                continue

            # publish camera image
            self._drone.publish_frame(img)

            # get face
            ret, f, x, y, w, h = self._face.detect_face(img)

            # face is found
            if ret:
                print('********** face is found **********')

                # remember the face
                self._face.set_template(f)

                return self._sm_follow_person


    def _sm_follow_person(self):
        while self.is_working():
            # get camera image
            ret, img = self._drone.subscribe_frame()
            if not ret:
                continue

            # get face
            ret, f, x, y, w, h = self._face.detect_template_face(img)

            # face is not found
            if not ret:
                print('********** face is lost **********')
                return self._sm_find_person

            # publish camera image
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
            self._drone.publish_frame(img)

            # current status
            area = self._face.wh2area(w, h)
            center = self._face.xywh2center(x, y, w, h)
            center_target = img.shape[1] // 2, img.shape[0] // 3
            #print('area', area)
            #print('center', center)

            # controll to adjust
            adj_x = 0.0
            adj_r = 0.0
            adj_z = 0.0
            if abs(area - self._area_target) > self._area_th:
                adj_x = self._vx if area < self._area_target     else -1 * self._vx
            if abs(center[0] - center_target[0]) > self._center_th:
                adj_r = self._vr if center[0] > center_target[0] else -1 * self._vr
            if abs(center[1] - center_target[1]) > self._center_th:
                adj_z = self._vz if center[1] < center_target[1] else -1 * self._vz

            #print(adj_x, adj_r, adj_z)
            if not self._debug:
                self._drone.controll(t=self._tg, vx=adj_x, vr=adj_r, vz=adj_z)


    def _sm_find_person(self, timeout=100):
        for t in range(timeout):
            # get camera image
            ret, img = self._drone.subscribe_frame()
            if not ret:
                continue

            # get face
            ret, f, x, y, w, h = self._face.detect_template_face(img)

            # face is re-found
            if ret:
                print('********** face is re-found **********')
                return self._sm_follow_person

        print('********** timeout, searching new face **********')
        return self._sm_remember_person


if __name__ == '__main__':
    fol = Follow(dbg=False)
    fol.execute()