# import system
import os
import json



class Calibration():

    from_pts = 'file' # exodus data
    from_data = ''
    calib_dta = {}

    def __init__(self, from_pts, from_data):
        self.from_pts = from_pts
        self.from_data = from_data

    def prepare(self, camera_lsit) :

        for camera in camera_list : 
            calib_dat[camera] = {}


    def parse_pts(self):
        json_data = self.json_data

        data = {
            "worlds": [],
            "points": []
        }

        data['worlds'] = json_data['worlds']
        cnt = 0

        # Store only the values of the necessary channels
        for dict_args in self.args:
            for dict_data in json_data['points']:
                if dict_args['camIdx'] == dict_data['dsc_id']:
                    print(dict_args['camIdx'])
                    print(dict_data['pts_3d']['X1'])
                    pts_3d = {"X1": 0, "Y1": 0, "X2": 0, "Y2": 0,
                              "X3": 0, "Y3": 0, "X4": 0, "Y4": 0}
                    pts_3d["X1"] = dict_data['pts_3d']['X1']
                    pts_3d["Y1"] = dict_data['pts_3d']['Y1']
                    pts_3d["X2"] = dict_data['pts_3d']['X2']
                    pts_3d["Y2"] = dict_data['pts_3d']['Y2']
                    pts_3d["X3"] = dict_data['pts_3d']['X3']
                    pts_3d["Y3"] = dict_data['pts_3d']['Y3']
                    pts_3d["X4"] = dict_data['pts_3d']['X4']
                    pts_3d["Y4"] = dict_data['pts_3d']['Y4']
                    data['points'].append({
                        "dsc_id": dict_data['dsc_id'],
                        "Group": dict_data['Group'],
                        "pts_3d": pts_3d
                    })

        return data
