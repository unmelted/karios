import os
from logger import Logger as l
import define as df
from db_layer import NewPool, DBLayer, BaseQuery


class DbManager(BaseQuery):
    # conn = NewPool().getConn()
    sql_list = BaseQuery.loadjson(None)

    @classmethod
    def status_update(cls, job_id, status):
        q = BaseQuery.update('command', status=status, job_id=job_id)
        result = DBLayer.queryWorker('update', q)
'''
    @classmethod
    def insert_newcommand(cls, job_id, parent_id, ip, task, input_dir, group, config1, config2):
        q = BaseQuery.insert('command', job_id=job_id, parent_job=parent_id, requestor=ip, task=task,
                             input_path=input_dir, group_name=group,  config1=config1, config2=config2)
        result = DBLayer.queryWorker('insert', q)

    @classmethod
    def update_command_pair(cls, image1, image2, job_id):
        q = BaseQuery.update('command', image_pair1=image1,
                             image_pair2=image2, job_id=job_id)
        result = DBLayer.queryWorker('update', q)

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

    @classmethod
    def insert_adjustData3(cls, job_id, parent_job, left, top, width, height):
        q = ''
        q = 'UPDATE adjust_data SET margin_left =%s, margin_top = %s, margin_width = %s, margin_height = %s WHERE job_id =%s and parent_job = %s;' % \
            (str(left), str(top), str(width), str(height), job_id, parent_job)
        l.get().w.info("update world Query {}".format(q))
        result = DBLayer.queryWorker('update', q)
'''