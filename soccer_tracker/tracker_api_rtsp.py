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

        CMPFUNC = CFUNCTYPE(c_void_p, POINTER(c_void_p), c_int, c_longlong, POINTER(c_char), c_int, c_longlong)

        cmp_func = CMPFUNC(self.frameCallBack)
        Mod.PlayUrl(cmp_func, RtspClient)

        while True:
            try:
                get_frame = self.frame_no
                get_image = self.get_img

                #test
                resize_img = cv2.resize(get_image, (1920,1080))
                ret, main_frame = cv2.imencode('.jpg', resize_img)



                # tracked, image_frame, loc_data = T.infer_single_frame_from_stream(raw_frame=get_image,vis=True)
                msg = {}
                msg['id'] = []
                msg['box'] = []
                msg['frame'] = []
                msg['lost_id'] = []
                msg['loc'] = []
                # resize_img = cv2.resize(image_frame, (1750, 300))
                # ret, main_frame = cv2.imencode('.jpg', resize_img)
                # msg['id'].append(0)
                # msg['box'].append([0,0,0,0])
                # msg['frame'].append(base64.b64encode(main_frame).decode('utf-8'))
                # msg['loc'].append([0,0])
                # msg['frame_id'] = get_frame
                # for i, tracked_data in enumerate(tracked.tracked_stracks):
                #     bbox = list(map(int,tracked_data.tlbr))
                #     msg['id'].append(tracked_data.track_id)
                #     msg['box'].append(bbox)
                #     msg['loc'].append(loc_data[i])
                #     cropped_frame = image_frame[bbox[1]+1:bbox[3],bbox[0]+1:bbox[2]]
                #     resize_frame = cv2.resize(cropped_frame, (50, 100))
                #     ret, cropped_img = cv2.imencode('.jpg', resize_frame)
                #     msg['frame'].append(base64.b64encode(cropped_img).decode('utf-8'))
                # await websocket.send(json.dumps(msg))
            except Exception as e:
                pass




    def frameCallBack(self, arg, frame_type, timestamp, buf, len, nReplayFramNum):

        ret = libfr.fr_decode_ex(handle, buf, len, nReplayFramNum, outVideo)

        try:
            tmp = ctypes.cast(outVideo.data, POINTER(ctypes.c_byte * 3 * outVideo.width * outVideo.height)).contents
            img = np.frombuffer(tmp, dtype=np.uint8)
            img = img.reshape(outVideo.height, outVideo.width, 3)
            print(type(img))
            # cv2.imshow("img test",img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
            self.frame_no = nReplayFramNum
            self.get_img = img
        except:
            pass




    def run(self):
        self.main()

rtsl = rtsp_lib()
rtsl.run()