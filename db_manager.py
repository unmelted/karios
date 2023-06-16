import os
import numpy as np

from logger import Logger as l
from define import Definition as defn
from db_layer import NewPool, DBLayer, BaseQuery


class DbManager(BaseQuery):
    # conn = NewPool().getConn()
    sql_list = BaseQuery.loadjson(None)

    @classmethod
    def status_update(cls, job_id, status):
        q = BaseQuery.update('command', status=status, job_id=job_id)
        result = DBLayer.queryWorker('update', q)

    @classmethod
    def getJobIndex(cls):
        index = 0
        rows = DBLayer.queryWorker('select-one',
                                   cls.sql_list['query_job_id'])

        if rows == None:
            return defn.base_index
        if len(rows) == 0:
            return defn.base_index

        index = rows[0]
        return index


    @classmethod
    def insert_newcommand(cls, job_id, exodus_job_id, task_id):
        q = BaseQuery.insert('command', job_id=job_id, task_id=task_id, exodus_job_id=exodus_job_id)
        result = DBLayer.queryWorker('insert', q)

    @classmethod
    def create_result_table(cls, table_name1, table_name2) :
        query = f"CREATE TABLE IF NOT EXISTS {table_name1} (frame_id INTEGER NOT NULL, createdate TIMESTAMP DEFAULT NOW(), camera_id TEXT, from_id TEXT, object_id TEXT, confidence REAL, team TEXT, x REAL, y REAL, width REAL, height REAL, detail TEXT, PRIMARY KEY (frame_id , camera_id, object_id))"
        
        result = DBLayer.queryWorker('create', query)

        # query = f"CREATE TABLE IF NOT EXISTS {table_name2} (no SERIAL, frame_id INTEGER PRIMARY KEY NOT NULL, object_id TEXT, team TEXT, x REAL, y REAL, width REAL, height REAL, detail TEXT)"

        # result = DBLayer.queryWorker('create', query)
        

    @classmethod
    def insert_tracker_info(cls, job_id, tracker_ip, stream_url):
        q = BaseQuery.insert('tracker_info', job_id=job_id, tracker_ip=tracker_ip, stream_url=stream_url)
        result = DBLayer.queryWorker('insert', q)

    @classmethod
    def update_tracker_info(cls, job_id, tracker_ip, type, data) :
        pass

    @classmethod
    def insert_que_result(cls, table_name, frame_id, camera_id, from_id, object) :
        print("insert que result .." , table_name, frame_id, camera_id, from_id)

        q = BaseQuery.insert(table_name, frame_id=frame_id, camera_id=camera_id, from_id=from_id, object_id=object['id'],
        confidence=0.0, team=object['team'], x=float(object['x']), y=float(object['y']), width=float(object['width']), height=float(object['height']))

        result = DBLayer.queryWorker('insert', q)


    @classmethod
    def check_result_table(cls, job_id) :
        table_name = defn.prefix + str(job_id)        
        q = 'SELECT EXISTS ( SELECT 1 FROM information_schema.tables WHERE table_name = ' + table_name + ');'

        print('check result table', table_name , q)
        result = DBLayer.queryWorker('select-one')
        print(result[0])

        return result[0]

    @classmethod
    def get_visual_info(cls, job_id) :
        try : 
            table_name = defn.prefix + str(job_id)
            base1 = 'WITH lower_precision as (SELECT DATE_TRUNC('second', createdate)::TIMESTAMP(0) as lower_precision_timestamp, frame_id FROM {} ) SELECT DISTINCT lower_precision_timestamp, frame_id FROM lower_precision WHERE (lower_precision_timestamp, frame_id) = (SELECT MIN(lower_precision_timestamp), MIN(frame_id) from lower_precision);'
            q1 = base.format(table_name)

            result1 = DBLayer.queryWorker('select-one')

            base2 = 'WITH lower_precision as (SELECT DATE_TRUNC('second', createdate)::TIMESTAMP(0) as lower_precision_timestamp, frame_id FROM {} ) SELECT DISTINCT lower_precision_timestamp, frame_id FROM lower_precision WHERE (lower_precision_timestamp, frame_id) = (SELECT MAX(lower_precision_timestamp), MAX(frame_id) from lower_precision);'
            q2 = base2.format(table_name)

            result2 = DBLayer.queryWorker('select-one')
        except : 
            return -116, 0, 0, 0, 0

        start_time = result1[0][0]
        start_frame = result1[0][1]
        end_time = result2[0][0]
        end_frame = result2[0][1]

        l.get().w.debug("get visual info return start time {} start frame {} end time {} end frame {} ".format(start_time, start_frame, end_tiem, end_frame))

        return 0, start_time, start_frame, end_time, end_frame

    @classmethod
    def get_players_data(cls, job_id, start_frame, end_frame) :
        table_name = defn.prefix + str(job_id)        
        data = None
        base = 'SELECT team, x, y FROM {} \
        WHERE frame_id > {} and frame_id < {} ORDER BY frame_id;'
        q = base.format(table_name, start_frame, end_Frame)
        data = DBLayer.queryWorker('select-all')

        arr_data = np.array(data)
        print("get_players_data : ", arr_data)

        return arr_data

    @classmethod
    def get_players_data_1frame(cls, job_id, target_frame):
        table_name = defn.prefix + str(job_id)        
        data = None
        base = 'SELECT team, x, y FROM {} \
        WHERE frame_id = {};'
        q = base.format(table_name, target_frame)
        data = DBLayer.queryWorker('select-all')

        arr_data = np.array(data)
        print("get_players_data_1frame : ", arr_data)

        return arr_data


'''
    @classmethod
    def getJobStatus(cls, id):
        q = cls.sql_list['query_status'] + str(id)
        l.get().w.info("Get Status Query: {} ".format(q))
        rows = DBLayer.queryWorker('select-all', q)

        if len(rows) > 1:
            return -201, 0
        elif len(rows) == 0:
            return -151, 0
        else:
            l.get().w.debug("status : {} {} ".format(
                str(rows[0][0]), str(rows[0][1])))
            # for row in rows :
            # print(row)

        return rows[0][0], rows[0][1]

'''