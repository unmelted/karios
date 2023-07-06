# import system
import os
import json
import requests
from requests.exceptions import RequestException
import asyncio
import cv2
import numpy as np

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

        l.get().w.debug("Calibration load data done. ", self.calib_raw_data[self.calib_id[0]])
        return result
    
    
    def load_data_file(self) :
        result = 0
        # filename = need to be changed for the environment..
        filename = self.calib_file.split('/Volumes', 1)[-1]
        print('load_data_file filename : ', filename)

        with open(filename, 'r') as json_file :
            self.calib_raw_data = json.load(json_file)
        
        if self.calib_raw_data == None :
            l.get().w.error('cant open the pts file')
            return -109

        return result 
        

    def get_points(self, camera_id, group, calib_job_id = None) :
        result = 0
        world = []
        pts = []
        world_pts = None
        pts_3d = None
        
        if self.calib_type == 'file' and self.calib_raw_data != None :
            result, world, pts = self.get_points_from_file(camera_id, group)

        elif self.calib_type == 'exodus' and self.calib_raw_data != None and calib_job_id != -1:
            result, world, pts = self.get_points_from_data(camera_id, group, calib_job_id)

        else :
            result = -111, 0, 0

        if result == 0 :
            # world_pts = np.array([[world[0], world[1]], 
            #                         [world[2], world[3]], 
            #                         [world[4], world[5]], 
            #                         [world[6], world[7]]])
            world_pts = np.array([[100, 100], 
                                    [200, 200], 
                                    [100, 500], 
                                    [500, 500]])
            pts_3d = np.array([[pts[0],pts[1]], 
                                [pts[2], pts[3]], 
                                [pts[4], pts[5]], 
                                [pts[6], pts[7]]])

        return result, world_pts, pts_3d


    def get_homography(self, base, pts_3d) :
        H = None
        result = 0

        try : 
            # print(base, pts_3d)
            H, ret = cv2.findHomography(base, pts_3d, cv2.RANSAC)

        except : 
            l.get().w.error('find homography cannot calcualte. maybe point error')
            result = -114

        return result, H

    def get_points_from_file( self, camera_id, group ) :
        result = 0
        world_pts = []
        pts_3d = []

        for i in range(len(self.calib_raw_data['worlds'])) :
            print("camera group == world group ", group, self.calib_raw_data['worlds'][i]['group'])            
            if self.calib_raw_data['worlds'][i]['group'] == group :

                world_pts.append(float(self.calib_raw_data['worlds'][i]['world_coords']['X1']))
                world_pts.append(float(self.calib_raw_data['worlds'][i]['world_coords']['Y1']))
                world_pts.append(float(self.calib_raw_data['worlds'][i]['world_coords']['X2']))
                world_pts.append(float(self.calib_raw_data['worlds'][i]['world_coords']['Y2']))
                world_pts.append(float(self.calib_raw_data['worlds'][i]['world_coords']['X3']))
                world_pts.append(float(self.calib_raw_data['worlds'][i]['world_coords']['Y3']))
                world_pts.append(float(self.calib_raw_data['worlds'][i]['world_coords']['X4']))
                world_pts.append(float(self.calib_raw_data['worlds'][i]['world_coords']['Y4']))
                break

        for j in range(len(self.calib_raw_data['points'])) :
            if self.calib_raw_data['points'][j]['dsc_id'] == camera_id :
                print("camera name == dsc_id ", camera_id, self.calib_raw_data['points'][j]['dsc_id'])
                pts_3d.append(float(self.calib_raw_data['points'][j]['pts_3d']['X1']))
                pts_3d.append(float(self.calib_raw_data['points'][j]['pts_3d']['Y1']))
                pts_3d.append(float(self.calib_raw_data['points'][j]['pts_3d']['X2']))
                pts_3d.append(float(self.calib_raw_data['points'][j]['pts_3d']['Y2']))
                pts_3d.append(float(self.calib_raw_data['points'][j]['pts_3d']['X3']))
                pts_3d.append(float(self.calib_raw_data['points'][j]['pts_3d']['Y3']))
                pts_3d.append(float(self.calib_raw_data['points'][j]['pts_3d']['X4']))
                pts_3d.append(float(self.calib_raw_data['points'][j]['pts_3d']['Y4']))

                break

        if len(world_pts) == 0 or len(pts_3d) == 0 :
            result = -112, 0, 0

        l.get().w.error('get_points_from_file return result {} world {} pts_3d {}'.format(result, world_pts, pts_3d))
        return result, world_pts, pts_3d


    def get_points_from_data(self, camera_id, group, calib_jod_id) :
        result = 0
        world_pts = []
        pts_3d = []

        # for j in range(len(self.calib_raw_data['worlds'])) :
        #     if self.calib_raw_data['world'][j]['group'] == group :
        #         print("camera name == dsc_id ", camera_id, self.calib_raw_data['world'][j]['world_coords'])
        #         world_pts.append(float(self.calib_raw_data['worlds'][j]['world_coords']['X1']))
        #         world_pts.append(float(self.calib_raw_data['worlds'][j]['world_coords']['Y1']))
        #         world_pts.append(float(self.calib_raw_data['worlds'][j]['world_coords']['X2']))
        #         world_pts.append(float(self.calib_raw_data['worlds'][j]['world_coords']['Y2']))
        #         world_pts.append(float(self.calib_raw_data['worlds'][j]['world_coords']['X3']))
        #         world_pts.append(float(self.calib_raw_data['worlds'][j]['world_coords']['Y3']))
        #         world_pts.append(float(self.calib_raw_data['worlds'][j]['world_coords']['X4']))
        #         world_pts.append(float(self.calib_raw_data['worlds'][j]['world_coords']['Y4']))

        for j in range(len(self.calib_raw_data[self.calib_id[0]]['points'])) :
            if self.calib_raw_data[self.calib_id[0]]['points'][j]['dsc_id'] == camera_id :
                print("camera name == dsc_id ", camera_id, self.calib_raw_data[self.calib_id[0]]['points'][j]['dsc_id'])
                pts_3d.append(float(self.calib_raw_data[self.calib_id[0]]['points'][j]['pts_3d']['X1']))
                pts_3d.append(float(self.calib_raw_data[self.calib_id[0]]['points'][j]['pts_3d']['Y1']))
                pts_3d.append(float(self.calib_raw_data[self.calib_id[0]]['points'][j]['pts_3d']['X2']))
                pts_3d.append(float(self.calib_raw_data[self.calib_id[0]]['points'][j]['pts_3d']['Y2']))
                pts_3d.append(float(self.calib_raw_data[self.calib_id[0]]['points'][j]['pts_3d']['X3']))
                pts_3d.append(float(self.calib_raw_data[self.calib_id[0]]['points'][j]['pts_3d']['Y3']))
                pts_3d.append(float(self.calib_raw_data[self.calib_id[0]]['points'][j]['pts_3d']['X4']))
                pts_3d.append(float(self.calib_raw_data[self.calib_id[0]]['points'][j]['pts_3d']['Y4']))

        # if len(world_pts) == 0 or len(pts_3d) == 0 :
        if len(pts_3d) == 0 :
            result = -112, 0, 0

        l.get().w.error('get_points_from_data return result {} world {} pts_3d {}'.format(result, world_pts, pts_3d))
        return result, world_pts, pts_3d



