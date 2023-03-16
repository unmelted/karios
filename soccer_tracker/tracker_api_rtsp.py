# import os
# import asyncio
# import ctypes
# import json
# import cv2
# import numpy as np
# import base64
# import sys
# import websockets
# from ctypes import CFUNCTYPE
# from ctypes import c_void_p
# from ctypes import c_char
# from ctypes import c_int
# from ctypes import c_uint
# from ctypes import Structure
# from ctypes import c_longlong
# from ctypes import POINTER


# # api_param = ""
# # rtsp_url = ""
# # locl_url = ""
# # websocket_port = ""


# # # api_param = sys.argv[1]
# # # rtsp_url = sys.argv[2]
# # # # use stadium size??
# # # locl_url = sys.argv[3]
# # # websocket_port = int(sys.argv[4])

# # coord_list = [int(i) for i in api_param.split(',')]


# class FfVideo(Structure):
#     _fields_ = (
#         ('data', POINTER(c_char)),
#         ('width', c_int),
#         ('height', c_int),
#         ('pitch', c_int),
#         ('cts', c_int),
#         ('idx', c_uint),
#     )


# print(os.getcwd())
# path = os.getcwd() + "\\rtsp_lib\\build\\librtspReceiver.so"
# print(path)
# Mod = ctypes.cdll.LoadLibrary(path)
# print(Mod)
# path_ff = "/workspace/rtsp_lib/libffpy.so"
# libfr = ctypes.cdll.LoadLibrary(path_ff)


# class rtsp_lib:

#     async def main(self, websocket):
#         global outVideo, handle, libfr, Mod

#         self.frame_no = None
#         self.get_img = None

#         path = os.getcwd() + '\\workspace\rtsp_lib\build\librtspReceiver.so'
#         Mod = ctypes.cdll.LoadLibrary(path)
#         print(Mod)
#         path_ff = "/workspace/rtsp_lib/libffpy.so"
#         libfr = ctypes.cdll.LoadLibrary(path_ff)

#     # async def handler(self, websocket):
#     #     await self.main(websocket)

#     # async def start(self):
#     #     async with websockets.serve(self.handler, locl_url, websocket_port):
#     #         await asyncio.Future()

#     # def run(self):
#     #     asyncio.run(self.start())


# rtsl = rtsp_lib()
# # rtsl.run()
