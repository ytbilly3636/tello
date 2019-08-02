#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../tello'))
from lib import StateMachine, ARDetector

import cv2
import time


class FollowAR(StateMachine):
    def __init__(self, 
        area_target = 10000, 
        area_th     = 1000, 
        center_th   = 100,
        tg          = 0.2,
        vx          = 0.1,
        vr          = 0.4,
        vz          = 0.4,
        dbg         = False
        ):
        super(FollowAR, self).__init__()
        self._state = self._sm_takeoff

        self._ar = ARDetector()

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
        return self._sm_find_marker


    def _sm_find_marker(self):
        while self.is_working():
            # get camera image
            ret, img = self._drone.subscribe_frame()
            if not ret:
                continue

            # get marker
            corns, ids = self._ar.detect_marker(img)

            # marker is found
            if ids is None:
                print('********** marker is found **********')
                return self._sm_follow_marker


    def _sm_follow_marker(self):
        while self.is_working():
            # get camera image
            ret, img = self._drone.subscribe_frame()
            if not ret:
                continue

            # get marker
            corns, ids = self._ar.detect_marker(img)

            # marker is not found
            if ids is None:
                print('********** marker is lost **********')
                return self._sm_find_marker

            # select marker
            corn_ = corns[0]
            id_ = ids[0]

            # current status
            area = self._ar.corn2area(corn_)
            center = self._ar.corn2center(corn_)
            center_target = img.shape[1] // 2, img.shape[0] // 2
            print(area)

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

            if not self._debug:
                self._drone.controll(t=self._tg, vx=adj_x, vr=adj_r, vz=adj_z)

            # publish camera image
            cv2.circle(img, (center[0], center[1]), 50, (0, 255, 0), -1)
            self._drone.publish_frame(img)


if __name__ == '__main__':
    fol = FollowAR(dbg=False)
    fol.execute()