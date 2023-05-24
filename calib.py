# import system
import os
import json
import requests
from requests.exceptions import RequestException
import asyncio

from logger import Logger as l
from db_manager import DbManager
from define import Definition as df
from define import RequestCategory as rc



class Calibration():

    calib_type = 'file' # or exodus
    calib_file = '' 
    calib_id = []
    calib_ddta = {} #camera_id : group_id, 3d point, world point

    calib_raw_data = {}

    def __init__(self, calib_type, calib_file, calib_id):
        l.get().w.debug("Calibration init type  {} \n file {} \n id {} ".format(calib_type, calib_file, calib_id))

        self.calib_type = calib_type
        self.calib_file = calib_file
        self.calib_id = calib_id


    def load_data(self) :
        result = 0
        if self.calib_type == 'file' and self.calib_file != '':
            result = self.load_data_file()

        elif self.calib_type == 'exodus' and len(self.calib_id) > 0 :
            data = {}
            for cid in self.calib_id :
                url = 'http://'+ df.exodus_ip + ':' + str(df.exodus_port) + df.exodus_cmd + 'getresult/' + str(cid)
                l.get().w.error(" Calibraiton data request from exodus url {}".format(url))

                try : 
                    response = requests.get(url)
                    json_response = response.json()

                    self.calib_raw_data[cid] = json_response['contents']

                except Exception as e : 
                    l.get().w.error('Calibraiton send to exodus GetResult but, error occurred {}'.format(str(e)))
                    result = -110
                    break

        l.get().w.debung("Calibration load data done. ", self.calib_raw_data)
        return result
    
    
    def load_data_file(self) :

        filename = self.calib_file.split('/')[1:]
        print('load_data_file filename : ', filename)

        with open(filename, 'r') as json_file :
            self.calib_raw_data = json.load(json_file)
        
        if self.calib_raw_data == None :
            l.get().w.error('cant open the pts file')
            return -109

        

    def get_points(self, camera_id, calib_job_id) :
        result = 0
        world_pts = []
        pts_3d = []
        
        if self.calib_type == 'file' and self.calib_raw_data != None :
            result, world_pts, pts_3d = self.get_points_from_file()

        else self.calib_type == 'exodus' and self.calib_raw_data != None and calib_job_id != -1:
            result, world_pts, pts_3d = self.get_points_from_data()

        else :
            result = -111
        return result, world_pts, pts_3d


    def get_points_from_file( self, camera_id ) :
        result = 0
        world_pts = []
        pts_3d = []

        for j in range(len(self.calib_raw_data['points'])) :
            if self.calib_raw_data['points'][j]['dsc_id'] == camera_id :
                print("camera name == dsc_id ", camera_id, self.calib_raw_data['points'][j]['dsc_id'])
                break

        if len(world_pts) == 0 or len(pts_3d) == 0 :
            result = -112

        return result, world_pts, pts_3d


    def get_points_from_data( self, camera_id, calib_jod_id) :
        result = 0
        world_pts = []
        pts_3d = []






