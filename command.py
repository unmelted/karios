import os
import time
from multiprocessing import Queue
import requests
import json

from logger import Logger as l
from task import TaskActivity
from db_manager import DbManager
from define import RequestCategory as rc
from tracker import MultiTracker

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
	def add_task(cls, category, task):
		print("commander add task is called ", category)

		if TaskActivity.checkJobsUnderLimit() is True:
			job_id = DbManager.getJobIndex() + 1
			cls.cmd_q.put((category, task, job_id))
			l.get().w.info("Alloc job id {} ".format(job_id))

			return job_id
		else:
			return -22

	@classmethod
	def add_msg(cls, url, data):
		print("commander add msg is called ", url, data)
		cls.cmd_q.put((url, data))

	@classmethod
	def receiver(cls) :

		while True :
			time.sleep(0.3)

			if (cls.cmd_q.empty() is False) :
				category, task, job_id = cls.cmd_q.get()
				Commander.processor(category, task, job_id)


	@classmethod
	def request_query(cls, query) :
		print("commander receive query ", task)
		result = 0
		status = 0
		contents = []



	@classmethod
	def processor(cls, category, task, job_id) :
		# result = 0 
		status = 0
		l.get().w.debug("task proc start : {}".format(job_id))

		if category == rc.TRACKER_READY :
			multi_tracker = MultiTracker(cls.msg_q)
			multi_tracker.prepare(task)

	@classmethod
	def receiver_msg(cls) :

		while True :
			time.sleep(0.3)

			if (cls.msg_q.empty() is False) :
				url, data = cls.msg_q.get()
				print(url)
				print("msg_q receive data : ", json.dumps(data))

				response = requests.post(url, json=data)

				if response.status_code == 200:
					print("response success: ", response)
				else : 
					print("response error : ", response)
