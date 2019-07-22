#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import tellopy
import av
import numpy as np
import cv2

import time
import concurrent.futures


class Drone(object):
    def __init__(self):
        self._drone = tellopy.Tello()
        self._drone.set_loglevel(0)

        # shutdown if False
        self._is_working = True

        # try to connect
        self._drone.connect()
        self._drone.wait_for_connection(60.0)
        self._container = av.open(self._drone.get_video_stream())

        # video
        self._frame = None
        self._frame_show = np.zeros((640, 480), dtype=np.uint8) 
        self._tpe = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self._tpe.submit(self._thread_get_frame)
        self._tpe.submit(self._thread_show_frame)


    def is_working(self):
        return self._is_working


    def done(self):
        self._is_working = False
        self.land()
        cv2.destroyAllWindows()
        cv2.waitKey(1)


    def takeoff(self):
        self._drone.takeoff()


    def land(self):
        self._drone.land()
        self._drone.quit()


    def controll(self, t=1.0, vx=0.0, vy=0.0, vz=0.0, vr=0.0):
        # map values into -100-100
        vx = int(np.clip(vx, -1, 1) * 100)
        vy = int(np.clip(vy, -1, 1) * 100)
        vz = int(np.clip(vz, -1, 1) * 100)
        vr = int(np.clip(vr, -1, 1) * 100)

        # set velocity
        self._drone.forward(vx)     if vx > 0 else self._drone.backward(abs(vx))
        self._drone.left(vy)        if vy > 0 else self._drone.left(abs(vy))
        self._drone.up(vz)          if vz > 0 else self._drone.down(abs(vz))
        self._drone.clockwise(vr)   if vr > 0 else self._drone.counter_clockwise(abs(vr))

        # wait
        time.sleep(t)

        # unset velocity
        self._drone.forward(0)
        self._drone.backward(0)
        self._drone.left(0)
        self._drone.left(0)
        self._drone.up(0)
        self._drone.down(0)
        self._drone.clockwise(0)
        self._drone.counter_clockwise(0)


    def _thread_get_frame(self):
        while self._is_working:
            for frame in self._container.decode(video=0):
                self._frame = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)


    def _thread_show_frame(self):
        while self._is_working:
            cv2.imshow('window', self._frame_show)
            key = cv2.waitKey(1)

            # forced termination
            if key & 0xFF == ord('q'):
                self.done()


    def subscribe_frame(self):
        ret = False if self._frame is None else True
        return ret, self._frame


    def publish_frame(self, x):
        self._frame_show = x