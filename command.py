import os
import time
from multiprocessing import Queue
import requests
import json
import asyncio

from logger import Logger as l
from task import TaskActivity
from db_manager import DbManager
from define import RequestCategory as rc
from tracker import TrackerGroup

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Commander(metaclass=Singleton) :
	
	cmd_q = Queue()
	msg_q = Queue()
	trck_q = []

	# @classmethod
	def get_cmdq(self) :
		return self.cmd_q

	@classmethod
	def get_msgq(self) :
		return self.msg_q

	# @classmethod
	def add_task(self, category, task):
		print("commander add task is called ", category, task)
		print("trck_q sizse in add task: ", len(Commander.trck_q))

		if category == rc.TRACKER_READY :
			if TaskActivity.checkJobsUnderLimit() is True:
				job_id = DbManager.getJobIndex() + 1
				# self.cmd_q.put((category, task, job_id))
				# l.get().w.info("Alloc job id {} ".format(job_id))
				self.processor(category, task, job_id)
				
				return job_id
			else:
				return -22
		elif category == rc.TRACKER_START :
			self.processor(category, None, task)

	# @classmethod
	def add_msg(self, url, data):
		print("commander add msg is called ", url, data)
		self.cmd_q.put((url, data))

	# @classmethod
	def receiver(self) :

		while True :
			time.sleep(0.3)

			if (self.cmd_q.empty() is False) :
				category, task, job_id = self.cmd_q.get()
				self.processor(category, task, job_id)


	# @classmethod
	def request_query(self, category, job_id) :
		print("commander receive query ", category, job_id)
		print("trck_q sizse : ", len(self.trck_q))

		result = None
		status = None

		return self.processor(category, None, job_id)
	'''
		if category == rc.TRACKER_START :
			print("tracker start.. ", self.trck_q)

			if len(self.trck_q) > 0 :
				for trck in self.trck_q :
					if (job_id == trck.job_id) :
						print("matched job id is : ", job_id, trck.job_id)
				result = 0
				status = 100

			else :
				result = 0
				status = -101

		elif category == rc.TRACKER_STOP :
			pass

		elif category == rc.TRACKER_FINISH :
			pass

		return result, status
	'''

	# @classmethod
	def processor(self, category, task, job_id) :
		result = 0 
		status = 0
		l.get().w.debug("task proc start : {}".format(job_id))
		print("processor  start : ", self, id(Commander.trck_q), len(Commander.trck_q))

		if category == rc.TRACKER_READY :
			trackers = TrackerGroup(self.msg_q, job_id)
			trackers.prepare(task)
			Commander.trck_q.append(trackers)
			print("add trck_q sizse : ", id(Commander.trck_q), len(Commander.trck_q))			
			print(self)

		elif category == rc.TRACKER_START :
			print("tracker start.. ", id(Commander.trck_q), len(Commander.trck_q))

			if len(self.trck_q) > 0 :
				for trck in Commander.trck_q :
					if (job_id == trck.job_id) :
						print("matched job id is : ", job_id, trck.job_id)
				result = 0
				status = 100

			else :
				result = 0
				status = -101
		
		print("processor end : ", self, id(Commander.trck_q), len(Commander.trck_q))					
		return result, status

	# @classmethod
	async def receiver_msg(self) :

		while True :
			time.sleep(0.3)

			if (self.msg_q.empty() is False) :
				url, data, callback = self.msg_q.get()
				print(url)
				print("msg_q receive data : ", json.dumps(data))
				print(callback)

				response = requests.post(url, json=data)

				if response.status_code == 200:
					print("response success: ", response)
					json_response = response.json()				
					callback(json_response)

				else : 
					print("response error : ", response)
