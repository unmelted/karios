import os
import psutil
import time
import subprocess
import json
from define import Definition as defn
from logger import Logger as l
from db_layer import NewPool, DBLayer, BaseQuery

class TaskManager(BaseQuery):

    # conn = NewPool().getConn()
    sql_list = BaseQuery.loadjson(None)

    @classmethod
    def Watcher(cls):
        while (True):
            time.sleep(2)
            TaskManager.check_pid()

    @classmethod
    def getActiveJobs(cls):
        count = 0
        jids = []
        pids = []
        q = cls.sql_list['query_getactivejobs']
        rows = DBLayer.queryWorker( 'select-all', q)

        if len(rows) == 0:
            return 0, 0, 0
        else:
            count = len(rows)

        for i in range(0, count):
            jids.append(rows[i][0])
            if rows[i][1] != 'None':
                pids.append(int(rows[i][1]))
            else:
                pids.append(-1)

        print("active jids : ", jids)
        print("active pids : ", pids)
        print("active pids count : ", count)
        return count, jids, pids

class TaskActivity(BaseQuery) :
    conn = NewPool().getConn()
    sql_list = BaseQuery.loadjson(None)

    @classmethod
    def countActiveJobs(cls):
        q = cls.sql_list['query_countactivejobs']
        l.get().w.info("Count activejobs Query: {} ".format(q))
        rows = DBLayer.queryWorker( 'select-one', q)

        if len(rows) == 0:
            return 0
        else:
            l.get().w.debug("active jobs : {} ".format(rows[0]))
            count = rows[0]

        return count

    @classmethod
    def checkJobsUnderLimit(cls):
        print("jobmanager check jobs under limit")
        curJobs = TaskActivity.countActiveJobs()
        print("cur jobs : ", curJobs)
        if curJobs < defn.task_limit:
            return True
        else:
            return False

 
    @classmethod
    def insertNewJob(cls, job_id, pid1=None):
        q = BaseQuery.insert('job_manager', job_id=job_id,
                             pid1=pid, complete='running')
        result = DBLayer.queryWorker( 'insert', q)

    @classmethod
    def updateJob(cls, job_id, type, param=None):
        if type == 'complete':
            q = BaseQuery.update('job_manager', complete='done',
                                 complete_date='NOW()', job_id=job_id)

        result = DBLayer.queryWorker( 'update', q)
