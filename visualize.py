import os
import numpy as np

from logger import Logger as l
from db_manager import DbManager
from define import Definition as defn


class Visualize() :
    unit_h = 1 / defn.horizontal_grid
    unit_v = 1 / defn.vertical_grid

    print(unit_h, unit_v)

    @classmethod
    def generate_heatmap(cls, job_id, start_frame, end_frame) :
        resutl = 0 
        grids = [[0 for _ in range(defn.horizontal_grid)] for _ in range(defn.vertical_grid)]         
        result, data = DbManager.get_players_data(job_id, start_frame, end_frame)

        if result < 0 :
            return result, None

        if len(data) > defn.visualize_data_limit :
            return -119, None

        for row in data :
            # print(row)
            # print("add +1 ", int(row[1]/unit_h), int(row[2]/unit_v))            
            grids[int(row[1]/cls.unit_v)][int(row[2]/cls.unit_h)] += 1

        print(grids)
        return result, grids

    @classmethod
    def generate_3d_data(cls, job_id, select_frame) :
        result = 0        
        grids = [[0 for _ in range(defn.horizontal_grid)] for _ in range(defn.vertical_grid)]            
        result, data = DbManager.get_players_3d_1frame(job_id, select_frame)

        if result < 0 :
            return result, None

        if len(data) > defn.visualize_data_limit :
            return -119, None

        for row in data :
            print(row)
            # print("add +1 ", int(row[1]/unit_h), int(row[2]/unit_v))            
            grids[int(row[1]/cls.unit_v)][int(row[2]/cls.unit_h)] += 1

        print(grids)
        return result, grids

    @classmethod
    def generate_2d_data(cls, job_id, select_frame) :
        result = 0        
        grids = [[0 for _ in range(defn.horizontal_grid)] for _ in range(defn.vertical_grid)]            
        result, data = DbManager.get_players_2d_1frame(job_id, select_frame)

        if result < 0 :
            return result, None

        for row in data :
            print(row)
            # print("add +1 ", int(row[1]/unit_h), int(row[2]/unit_v))            
            grids[int(row[1]/cls.unit_v)][int(row[2]/cls.unit_h)] += 1

        print(grids)
        return result, grids

        return result, data

