#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import cv2
import six
import copy

import sys
import os


class YOLO(object):
    def __init__(self):
        # check cfg file
        cfg_path = os.path.join(os.path.dirname(__file__), 'yolov3.cfg')
        if not os.path.exists(cfg_path):
            sys.exit('Could not find lib/yolov3.cfg')

        # check weight file
        weights_path = os.path.join(os.path.dirname(__file__), 'yolov3.weights')
        if not os.path.exists(weights_path):
            sys.exit('Could not find lib/yolov3.weights')

        # load net
        self._net = cv2.dnn.readNetFromDarknet(cfg_path, weights_path)

        # output layer
        self._ln = self._net.getLayerNames()
        self._ln = [self._ln[i[0] - 1] for i in self._net.getUnconnectedOutLayers()]

        # labels
        label_path = os.path.join(os.path.dirname(__file__), 'coco.names')
        if not os.path.exists(label_path):
            sys.exit('Could not find lib/coco.names')
        
        self._label = open(label_path).read().strip().split('\n')
        self._color = self._generate_n_colors(len(self._label))
    

    def _generate_n_colors(self, n):
        colors = []

        for i in six.moves.range(n):
            hsv_img = np.zeros((1, 1, 3), dtype=np.uint8)

            hsv_img[0][0][0] = int(180 * i / n)
            hsv_img[0][0][1] = 255
            hsv_img[0][0][2] = 255

            rgb_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
            colors.append((int(rgb_img[0][0][0]), int(rgb_img[0][0][1]), int(rgb_img[0][0][2])))
        
        return colors


    def detect(self, frame, threshold=0.9):
        # width & height
        width  = frame.shape[1]
        height = frame.shape[0]

        # set input
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self._net.setInput(blob)

        # forward prop
        outputs = self._net.forward(self._ln)

        # lists for return
        boxes = []
        confs = []
        ids   = []

        # find high confidence object
        for out in outputs:
            for detection in out:
                class_id = np.argmax(detections[5:])
                conf = detections[5:][class_id]

                # skip low confidence
                if conf < threshold:
                    continue

                # bounding box
                box = detection[0:4] * np.array([width, height, width, height])
                box = box.astype(np.int32)
                w = box[2]
                h = box[3]
                x = box[0] - w // 2
                y = box[1] - h // 2

                # add
                boxes.append([x, y, w, h])
                confs.append(conf)
                ids.append(class_id)

        return boxes, confs, ids


    def draw_boxes(self, frame, boxes, ids):
        img = copy.deepcopy(frame)

        for box, class_id in zip(boxes, ids):
            cv2.rectangle(img, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]), self._color[class_id], 1)
            cv2.putText(img, self._label[class_id], (box[0], box[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, self._color[class_id], 1, cv2.LINE_AA)

        return img