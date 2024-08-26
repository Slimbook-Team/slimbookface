#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import struct
import fcntl

VIDIOC_QUERYCAP = 0x80685600

CAP_VIDEO_CAPTURE = 0x00000001

class Info:
    def __init__(self, data):
        self.driver = data[0].decode("utf-8")
        self.card = data[1].decode("utf-8")
        self.bus = data[2].decode("utf-8")
        self.version = data[3]
        self.caps = data[4]
        self.device_caps = data[5]

def query_capabilities(filename):
    fd = open(filename)
    data = struct.pack("104s",b"0"*104)
    out = fcntl.ioctl(fd, VIDIOC_QUERYCAP, data)
    info = struct.unpack("16s32s32sIII3I", out)
    fd.close()
    
    return Info(info)
