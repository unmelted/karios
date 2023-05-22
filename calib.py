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

    from_pts = 'file' # exodus data
    from_data = '' 
    calib_dta = {} #camera_id : group_id, 3d point, world point

    def __init__(self, job_id, group_id):


