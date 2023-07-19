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
        query1 = f"CREATE TABLE IF NOT EXISTS {table_name1} (no SERIAL, createdate TIMESTAMP DEFAULT NOW(), frame_id INTEGER NOT NULL, camera_id TEXT, object_id TEXT, team TEXT, x REAL, y REAL, width REAL, height REAL)"

        result = DBLayer.queryWorker('create', query1)
        
        query2 = f"CREATE TABLE IF NOT EXISTS {table_name2} (frame_id INTEGER NOT NULL, createdate TIMESTAMP DEFAULT NOW(), camera_id TEXT, from_id TEXT, object_id TEXT, confidence REAL, team TEXT, x REAL, y REAL, width REAL, height REAL, detail TEXT, PRIMARY KEY (frame_id , camera_id, object_id))"
        
        result = DBLayer.queryWorker('create', query2)


    @classmethod
    def insert_tracker_info(cls, job_id, tracker_ip, stream_url):
        q = BaseQuery.insert('tracker_info', job_id=job_id, tracker_ip=tracker_ip, stream_url=stream_url)
        result = DBLayer.queryWorker('insert', q)

    @classmethod
    def update_tracker_info(cls, job_id, tracker_ip, type, data) :
        pass

    @classmethod
    def insert_que_result_2d(cls, table_name, frame_id, camera_id, object) :
        print("insert que result1 .." , table_name, frame_id, camera_id )

        q = BaseQuery.insert(table_name, frame_id=frame_id, camera_id=camera_id, object_id=object['id'],
        team=object['team'], x=float(object['x']), y=float(object['y']), width=float(object['width']), height=float(object['height']))

        result = DBLayer.queryWorker('insert', q)


    @classmethod
    def insert_que_result_3d(cls, table_name, frame_id, camera_id, from_id, object) :
        print("insert que result2 .." , table_name, frame_id, camera_id, from_id)

        q = BaseQuery.insert(table_name, frame_id=frame_id, camera_id=camera_id, from_id=from_id, object_id=object['id'],
        confidence=0.0, team=object['team'], x=float(object['x']), y=float(object['y']), width=float(object['width']), height=float(object['height']))

        result = DBLayer.queryWorker('insert', q)

    @classmethod
    def check_result_table(cls, job_id) :
        _, table_name = defn.get_table_name(job_id)
        table_name = 'kairos_269'
        q = 'SELECT EXISTS ( SELECT 1 FROM information_schema.tables WHERE table_name = \'' + table_name + '\');'

        print('check result table', table_name , q)
        result = DBLayer.queryWorker('select-one', q)
        print(result[0])

        return result[0]

    @classmethod
    def get_visual_info(cls, job_id) :

        try : 
            _, table_name = defn.get_table_name(job_id)            
            table_name = 'kairos_269'
            query1 = f"WITH lower_precision as (SELECT DATE_TRUNC('second', createdate)::TIMESTAMP(0) as lower_precision_timestamp, frame_id FROM {table_name} ) SELECT DISTINCT lower_precision_timestamp, frame_id FROM lower_precision WHERE (lower_precision_timestamp, frame_id) = (SELECT MIN(lower_precision_timestamp), MIN(frame_id) from lower_precision)"

            result1 = DBLayer.queryWorker('select-one', query1)

            query2 = f"WITH lower_precision as (SELECT DATE_TRUNC('second', createdate)::TIMESTAMP(0) as lower_precision_timestamp, frame_id FROM {table_name} ) SELECT DISTINCT lower_precision_timestamp, frame_id FROM lower_precision WHERE (lower_precision_timestamp, frame_id) = (SELECT MAX(lower_precision_timestamp), MAX(frame_id) from lower_precision)"

            result2 = DBLayer.queryWorker('select-one', query2)

        except : 
            return -116, 0, 0, 0, 0

        print(result1[0])
        print(result2[0])

        start_time = result1[0]
        start_frame = result1[1]
        end_time = result2[0]
        end_frame = result2[1]

        l.get().w.debug("get visual info return start time {} start frame {} end time {} end frame {} ".format(start_time, start_frame, end_time, end_frame))

        return 0, start_time, start_frame, end_time, end_frame

    @classmethod
    def get_players_data(cls, job_id, start_frame, end_frame) :

        _, table_name = defn.get_table_name(job_id)            
        table_name = 'kairos_269'
        
        base = 'SELECT team, x, y FROM {} WHERE frame_id > {} and frame_id < {} ORDER BY frame_id;'
        q = base.format(table_name, start_frame, end_frame)
        rows = DBLayer.queryWorker('select-all', q)

        if rows == None or len(rows) == 0 :
            return -118, 0

        print("get_players_data : ", rows)
        return 0, rows

    @classmethod
    def get_players_3d_1frame(cls, job_id, target_frame):
        _, table_name = defn.get_table_name(job_id)        
        table_name = 'kairos_269'

        data = None
        base = 'SELECT team, x, y FROM {} WHERE frame_id = {};'
        q = base.format(table_name, target_frame)
        rows = DBLayer.queryWorker('select-all', q)

        if rows == None or len(rows) == 0 :
            return -118, 0

        print("get_players_data_1frame : ", rows)
        return 0, rows

    @classmethod
    def get_players_2d_1frame(cls, job_id, target_frame):
        table_name, _ = defn.prefix + str(job_id) + '_3d'        
        table_name = 'kairos_269'
        
        data = None
        base = 'SELECT team, x, y FROM {} \
        WHERE frame_id = {};'
        q = base.format(table_name, target_frame)
        rows = DBLayer.queryWorker('select-all', q)

        if rows == None or len(rows) == 0 :
            return -118, 0

        print("get_players_data_1frame : ", rows)
        return 0, rows


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