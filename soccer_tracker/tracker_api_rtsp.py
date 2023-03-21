import os
import asyncio
import ctypes
import json
import cv2
import numpy as np
import base64
import sys
import websockets
from ctypes import CFUNCTYPE
from ctypes import c_void_p
from ctypes import c_char
from ctypes import c_int
from ctypes import c_uint
from ctypes import Structure
from ctypes import c_longlong
from ctypes import POINTER



rtsp_url = sys.argv[1]


class FfVideo(Structure):
    _fields_ = (
        ('data', POINTER(c_char)),
        ('width', c_int),
        ('height', c_int),
        ('pitch', c_int),
        ('cts', c_int),
        ('idx', c_uint),
    )

class rtsp_lib:
    def main(self):
        print("rtsp_lib class is created")
        global outVideo, handle, libfr, Mod

        self.frame_no = None
        self.get_img = None

        print(os.getcwd())
        path = "./rtsp_lib/build/librtspReceiver.so"
        Mod = ctypes.cdll.LoadLibrary(path)
        path_ff = "./rtsp_lib/libffpy.so"
        libfr = ctypes.cdll.LoadLibrary(path_ff)
        print('check mod')

        libfr.fr_open.argtypes = [c_int, c_int]
        libfr.fr_open.restype = c_void_p
        libfr.fr_decode_ex.argtypes = [c_void_p, POINTER(c_char), c_int, c_uint, POINTER(FfVideo)]
        libfr.fr_decode_ex.restype = c_int
        libfr.fr_close.argtypes = [c_void_p]
        libfr.fr_close.restype = c_int

        outVideo = FfVideo()
        handle = libfr.fr_open(3840,2160)

        RtspClient = Mod.RtspClient_new()
        Mod.OpenURL(RtspClient, bytes(rtsp_url, 'utf-8'), 20)

       


    def run(self):
        self.main()

rtsl = rtsp_lib()
rtsl.run()