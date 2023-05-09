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
    def check_pid(cls):
        count, jids, pids = TaskManager.getActiveJobs()
        if count == 0:
            return 0

        cids = TaskManager.getCancelJobs()
        if len(cids) == 0:
            return 0

        for i in range(len(jids)):
            p = None
            job_id = jids[i]
            if job_id in cids:
                TaskManager.cancelProcess(job_id, pid)

        return 0

    @ classmethod
    def getCancelJobs(cls):
        cids = []
        q = TaskManager.sql_list['query_getcanceljobs']

        rows = DBLayer.queryWorker( 'select-all', q)

        for i in range(len(rows)):
            cids.append(int(rows[i][0]))

        print("getCancelJob : ", cids)
        return cids

    @ classmethod
    def cancelProcess(cls, job_id, pid):
            
        if pid < 0:
            l.get().w.critical("cancel malfuction minus pid: {} ".format(job_id))

        try:
            p = psutil.Process(pid)
            print(p)
            p.terminate()
            l.get().w.critical("---------------------cancel process : {}".format(pid))
            time.sleep(1)
        except psutil.NoSuchProcess:
            l.get().w.critical("No such process pid {}. already disappeared.".format(pid))

        except psutil.AccessDenied:
            l.get().w.critical("Acess Deineid to SystemProcess")
            result = -23

        # q = self.sql_list['query_deletejobs'] + str(job_id)
        # l.get().w.debug("delte jobs Query: {} ".format(q))
        # self.cursur2.execute(q)
        # cls.conn2.commit()
        # pid += 1
        # cmd = 'kill -9 `pgrep -f colmap -P ' + str(pid) +'`'
        # clear = os.system(cmd)
        # l.get().w.critical("Kill cmd -- {} : result {}".format(cmd, clear))
        q = BaseQuery.update('job_manager', cancel='done',
                             cancel_date='NOW()', complete='done', complete_date='NOW()', job_id=job_id)                             
        result = DBLayer.queryWorker( 'update', q)
        q = BaseQuery.update('command', result_id=-25, result_msg='Canceled Job', terminate=1, job_id=job_id)
        result = DBLayer.queryWorker( 'update', q)

        return 0

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
    def pushCancelJob(cls, job_id):
        q = BaseQuery.update('job_manager', cancel='try', job_id=job_id)
        result = DBLayer.queryWorker( 'update', q)

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
    def checkJobStatusForCancel(cls, job_id):
        q = cls.sql_list['query_jobstatusforcancel'] + str(job_id)
        l.get().w.info("Jobstatus Query before cancel: {} ".format(q))
        print(q)
        rows = DBLayer.queryWorker( 'select-one', q)

        print(rows[0], rows[1], rows[2])
        if len(rows) == 0:
            return -151
        else:
            # cancel / complete / pid2
            if rows[0] == None and rows[1] == 'running' and rows[2] != None:
                return 0
            else:
                if rows[0] != None:
                    return -401
                if rows[2] == None:
                    return -402
                return -202

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
