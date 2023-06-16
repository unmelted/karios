import os
import numpy as np

from logger import Logger as l
from db_manager import DbManager
from define import Definition as defn


class Visualize() :

    @classmethod
    def generate_heatmap(cls, job_id, start_frame, end_frame) :
        data = DbManager.get_players_data(job_id, start_frame, end_frame)
        #data format
        # createdate (sec) - team
        pass

    @classmethod
    def generate_3d_data(cls, job_id, select_frame) :
        pass

    @classmethod
    def generate_debug_data(cls, job_id, select_frame) :
        pass
