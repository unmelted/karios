import os
import time
from multiprocessing import Process, Queue
import threading
import requests
import json
import asyncio
from queue import Empty

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


class TrackerStock() :

	storage = {}

	def store(self, key, instance ):
		key = str(key)		
		self.storage[key] = instance 
		print("store : ", key)
		print(self.storage[key])

	def revmoe (self, key) :
		key = str(key)
		if key in self.storage:
			del self.storage[key]
		else :
			print(f"There is no key in storage '{key}'")

	def get_instance(self, key) :
		print("get instance : ", key)
		key = str(key)
		print(self.storage[key])
		return self.storage[key]


class Commander(metaclass=Singleton) :
	
	cmd_q = Queue()
	msg_q = Queue()
	task_stock = {}
	trck_q = TrackerStock()

	def start_commander(self) :
		print("start_commander ---------------------")

		def receiver_msg() :
			while True :
				time.sleep(0.3)
				print(".")

				if (self.msg_q.empty() is False) :
					url, type, data, job_type, job_id, cam_id = self.msg_q.get()
					print(url)
					print("msg_q receive data : ", json.dumps(data))

					# if type == 'POST' :
					# 	response = requests.post(url, json=data)
					# elif type == 'PUT':
					# 	response = requests.put(url)
					# elif type == 'GET' :
					# 	response = requests.get(url)

					# json_response = response.json()				
					json_response = {'error_code': 2000, 'error_msg': 'success', 'status': 'ready'}				
					print("response success: ", json_response)				
					# callback(job_type, cam_id, json_response)
					self.msg_callback(job_type, job_id, cam_id, json_response)

		thread = threading.Thread(target=receiver_msg)
		thread.start()
		print("commander end")


	def add_task(self, category, task):
		print("commander add task is called ", category, task)

		result = None
		status = 0

		if category == rc.TRACKER_READY :
			if TaskActivity.checkJobsUnderLimit() is True:
				job_id = DbManager.getJobIndex() + 1
				result, status = self.processor(category, task, job_id)
				if result == 0 : 
					result = job_id
					status = 0

			else:
				result = None
				status =  -22

		elif category == rc.TRACKER_START :
			result, status = self.processor(category, None, task)

		return result, status

	def add_msg(self, url, data):
		print("commander add msg is called ", url, data)
		self.cmd_q.put((url, data))


	def processor(self, category, task, job_id) :
		result = 0 
		status = 0
		l.get().w.debug("task processor start  cateory {} job_id {}".format(category, job_id))


		if category == rc.TRACKER_READY :
			trackers = TrackerGroup(self.msg_q, task['task_id'], job_id)
			trackers.prepare(task)
			DbManager.insert_newcommand(job_id, 0, task['task_id'])
			self.trck_q.store(job_id, trackers)			
			# self.trck_q.append(trackers)


		elif category == rc.TRACKER_START :

			trcks = self.trck_q.get_instance(job_id)
			result, status = trcks.start()
		

		l.get().w.debug("task processor end  cateory {} job_id {}".format(category, job_id))		
		return result, status

	
	def msg_callback(self, type, job_id, camera_id, data) :
		print("recive message callback " , type, camera_id, data)
		trcks = self.trck_q.get_instance(job_id)

		# for trcks in self.trck_q :
			# if trcks.job_id == job_id :
		for trck in trcks.trackers : 
			if trck.camera_id == camera_id :
				print("match . process... ")
				trck.step = 'READY_OK'
