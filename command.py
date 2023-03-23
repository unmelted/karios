import os
from multiprocessing import Queue


class Commander() :
	
	cmd_q = Queue()
	msg_q = Queue()

	@classmethod
	def get_cmdq(cls) :
		return cls.cmd_q

	@classmethod
	def get_msgq(cls) :
		return cls.msg_q

    @classmethod
    def add_task(cls, task):
        print("commander add task is called ", cls.cmd_q)

        if TaskActivity.checkJobsUnderLimit() is True:
            job_id = DbManager.getJobIndex() + 1
            cls.cmd_q.put((task, job_id))
            l.get().w.info("Alloc job id {} ".format(job_id))

            return job_id
        else:
            return -22

	@classmethod
	def receiver(cls) :
		while True :
			time.sleep(0.2)

			if (cls.cmd_q.emtpy() is False) :
				task = que.get()

	@classmethod
	def request_query(cls, query) :
		print("commander receive query ", task)
		result = 0
		status = 0
		contents = []

		if query['category'] == RequestCategory.GET_VERSION :
			print(Definition.get_version())



	@classmethod
	def processor(cls, task, job_id) :
		result = 0 
		status = 0
		l.get().w.debug("task proc start : {}".format(job_id))

		if task['category'] == RequestCategory.CONNECT_STREAM :
			print(task) 
