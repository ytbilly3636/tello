# tello

## Requirements

* tellopy
* cv2
    * libopencv-dev
* av
    * libavdevice-dev
    * libavfilter-dev
* chainer

### Python3 on Debian 9 as WSL

```sh
# Python3
$ apt-get update
$ apt-get install python3-dev python3-pip

# tellopy
$ pip3 install tellopy

# opencv
$ apt-get install libopencv-dev
$ pip3 install opencv-python

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
$ pip install opencv-python

# av
$ conda install av -c conda-forge

# chainer
$ pip install chainer
```
