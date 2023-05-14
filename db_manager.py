import os
from logger import Logger as l
from define import Definition as df
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
            return df.base_index
        if len(rows) == 0:
            return df.base_index

        index = rows[0]
        return index


    @classmethod
    def insert_newcommand(cls, job_id, exodus_job_id, task_id):
        q = BaseQuery.insert('command', job_id=job_id, task_id=task_id, exodus_job_id=exodus_job_id)
        result = DBLayer.queryWorker('insert', q)

    @classmethod
    def insert_tracker_info(cls, job_id, tracker_ip, stream_url):
        q = BaseQuery.insert('tracker_info', job_id=job_id, tracker_ip=tracker_ip, stream_url=stream_url)
        result = DBLayer.queryWorker('insert', q)

    @classmethod
    def update_tracker_info(cls, job_id, tracker_ip, type, data) :
        pass

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