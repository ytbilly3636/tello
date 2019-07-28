# tello

## Requirements

* tellopy
* cv2
    * libopencv-dev
* av
    * libavdevice-dev
    * libavfilter-dev
* chainer

### Debian 9 / Ubuntu 18.04

```sh
# Python3
$ apt-get update
$ apt-get install python3-dev python3-pip

# tellopy
$ pip3 install tellopy

# opencv
$ apt-get install libopencv-dev
$ pip3 install opencv-python opencv-contrib-python

# av
$ apt-get install libavdevice-dev libavfilter-dev
$ pip3 install av

# chainer
$ pip3 install chainer
```

### Anaconda

```sh
# tellopy
$ pip install tellopy

# opencv
$ pip install opencv-python opencv-contrib-python

# av
$ conda install av -c conda-forge

# chainer
$ pip install chainer
```

## Quick Start
Tello finds the nearest face and track the face.

```sh
$ python3 sample/follow.py
```
