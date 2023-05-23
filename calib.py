# import system
import os
import json
import requests
from requests.exceptions import RequestException
import asyncio

from logger import Logger as l
from db_manager import DbManager
from define import RequestCategory as rc



class Calibration():

    calib_type = 'file' # or exodus
    calib_file = '' 
    calib_id = []
    calib_ddta = {} #camera_id : group_id, 3d point, world point

    def __init__(self, calib_type, calib_file, calib_id):
        self.calib_type = calib_type
        self.calib_file = calib_file
        self.calib_id = calib_id



