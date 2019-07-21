#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../tello'))
from lib import StateMachine, FaceDetector


class Follow(StateMachine):
    def __init__(self, area_target=30000, area_th=5000, center_th=100):
        super(Follow, self).__init__()
        self._state = self._sm_takeoff

        self._face = FaceDetector()
        self._area_target = area_target
        self._area_th = area_th
        self._center_th = center_th


    def _sm_takeoff(self):
        print('********** take off **********')
        self._drone.takeoff()
        return self._sm_find_person


    def _sm_find_person(self):
        # get camera image
        ret, img = self._drone.get_camera()
        if not ret:
            return self._sm_find_person

        # get face
        ret, f, x, y, w, h = self._face.detect_face(img)

        # face is found
        if ret:
            print('********** face is found **********')
            return self._sm_follow_person

        # face is not found
        self._drone.controll(t=1.0, vr=0.1)
        return self._sm_find_person


    def _sm_follow_person(self):
        # get camera image
        ret, img = self._drone.get_camera()
        if not ret:
            return self._sm_find_person

        # get face
        ret, f, x, y, w, h = self._face.detect_face(img)

        # face is not found
        if not ret:
            print('********** face is lost **********')
            return self._sm_find_person

        # current status
        area = self._face.wh2area(w, h)
        center = self._face.xywh2center(x, y, w, h)
        center_target = img.shape[1] // 2, img.shape[0] // 2
        print('area', area)
        print('center', center)

        # controll to adjust
        adj_x = 0.0
        adj_y = 0.0
        adj_z = 0.0
        if abs(area - self._area_target) > self._area_th:
            adj_x = 0.1 if area < self._area_target     else -0.1
        if abs(center[0] - center_target[0]) > self._center_th:
            adj_y = 0.1 if center[0] < center_target[0] else -0.1 
        if abs(center[1] > center_target[1]) > self._center_th:
            adj_z = 0.1 if center[1] < center_target[1] else -0.1
        self._drone.controll(t=0.5, vx=adj_x, vy=adj_y, vz=adj_z)

        return self._sm_follow_person


if __name__ == '__main__':
    fol = Follow()
    fol.execute()