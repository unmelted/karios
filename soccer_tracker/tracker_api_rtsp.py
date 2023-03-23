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
import time



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
        self.check_num = 0
        print("rtsp_lib class is created")
        global outVideo, handle, libfr, Mod

        self.frame_no = None
        self.get_img = None

        path = "./rtsp_lib/build/librtspReceiver.so"
        Mod = ctypes.cdll.LoadLibrary(path)
        path_ff = "./rtsp_lib/libffpy.so"
        libfr = ctypes.cdll.LoadLibrary(path_ff)
        print('check mod')

        start = time.time()
        libfr.fr_open.argtypes = [c_int, c_int]
        libfr.fr_open.restype = c_void_p
        libfr.fr_decode_ex.argtypes = [c_void_p, POINTER(c_char), c_int, c_uint, POINTER(FfVideo)]
        libfr.fr_decode_ex.restype = c_int
        libfr.fr_close.argtypes = [c_void_p]
        libfr.fr_close.restype = c_int
        end = time.time()
        print(f"{end-start: .5f} sec ======> init 1")

        start = time.time()
        outVideo = FfVideo()
        handle = libfr.fr_open(3840,2160)
        end = time.time()
        print(f"{end - start: .5f} sec ======> fr_open")
        start = time.time()

        RtspClient = Mod.RtspClient_new()
        Mod.OpenURL(RtspClient, bytes(rtsp_url, 'utf-8'), 20)

        CMPFUNC = CFUNCTYPE(c_void_p, POINTER(c_void_p), c_int, c_longlong, POINTER(c_char), c_int, c_int)

        cmp_func = CMPFUNC(self.frameCallBack)
        Mod.PlayUrl(cmp_func, RtspClient)

        end = time.time()
        print(f"{end - start: .5f} sec ======> Mod")

        while True:
            try:
                get_frame = self.frame_no
                get_image = self.get_img
                # print("while testing... frame : ",get_frame)

                #test
                # resize_img = cv2.resize(get_image, (960,540))
                # print(type(get_image))
                # ret, main_frame = cv2.imencode('.jpg', resize_img)
                # cv2.imshow("img test",resize_img)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break

                if self.check_num == 100:
                    break

            except Exception as e:
                pass




        cv2.destroyAllWindows()



    def frameCallBack(self, arg, frame_type, timestamp, buf, len, nReplayFramNum):

        start = time.time()
        ret = libfr.fr_decode_ex(handle, buf, len, nReplayFramNum, outVideo)
        end = time.time()
        print(f"{(end - start)*1000} ms ======> fr_decode_ex ")
        # print("framecallback : ", nReplayFramNum)

        try:
            start = time.time()
            tmp = ctypes.cast(outVideo.data, POINTER(ctypes.c_byte * 3 * outVideo.width * outVideo.height)).contents
            img = np.frombuffer(tmp, dtype=np.uint8)
            img = img.reshape(outVideo.height, outVideo.width, 3)
            self.frame_no = nReplayFramNum
            self.get_img = img
            end = time.time()
            print(f"{(end - start) * 1000} ms ======> try ")
        except:
            pass

        # end = time.time()
        # print(f"{(end - start)*1000} ms ======> frameCallBack ")
        self.check_num += 1
        print(self.check_num)
        if self.check_num == 100:
            sys.exit()
            sys.exit("exit")




    def run(self):
        self.main()

rtsl = rtsp_lib()
rtsl.run()