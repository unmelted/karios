import os
import time
import datetime
from multiprocessing import Process, Queue
import threading
import requests
from requests.exceptions import RequestException
import json
import asyncio
from queue import Empty

from logger import Logger as l
from task import TaskActivity
from db_manager import DbManager
from define import RequestCategory as rc
from tracker import TrackerGroup
from visualize import Visualize


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
		l.get().w.debug("TrackerStock store key : {}".format(key))

	def remove (self, key) :
		key = str(key)
		if key in self.storage:
			del self.storage[key]
		else :
			l.get().w.debug("TrackerStock There is no key {}in storage. ".format(key))
		l.get().w.debug("TrackerStock remove {} in storage. ".format( key))

	def checking(self, key) :
		key = str(key)
		if key in self.storage :
			return False
		else :
			return True

	def get_instance(self, key) :
		key = str(key)

		if key in self.storage :
			l.get().w.debug("TrackerStock return instance {} in storage. ".format(key))			
			return self.storage[key]
		else :
			l.get().w.debug("TrackerStock There is no key {} in storage. ".format(key))
			return None

		return None


class Commander(metaclass=Singleton) :
	
	cmd_q = Queue()
	msg_q = Queue()
	task_stock = {}
	trck_q = TrackerStock()

	def start_commander(self) :
		l.get().w.debug("Commander Start.")

		def receiver_msg() :
			internal = False

			while True :
				time.sleep(0.3)
				# print(".")

				if (self.msg_q.empty() is False) :
					url, type, data, job_type, job_id, cam_id = self.msg_q.get()
					l.get().w.debug("Commander receive request url {} \n type {} \n job_type {} \n job_id {}".format(
						url, type, job_type, job_id))

					if internal == True :
						json_response = {'error_code': 2000, 'error_msg': 'success', 'status': job_type}
					else : 
						response = self.request_processor(url, type, data)
						if response == -1 :
							json_response = {'error_code': -201, 'error_msg': 'fail', 'status': ''}
						else : 
							json_response = response.json()


					l.get().w.debug("Commander receive request response : {}".format(json_response))
					self.msg_callback(job_type, job_id, cam_id, json_response)

		thread = threading.Thread(target=receiver_msg)
		thread.start()

	def request_processor(self, url, type, data) :

		l.get().w.debug("Commander request_processor : {}".format(url))

		response = -1
		try:
			if type == 'POST':
				response = requests.post(url, json=data)								

			elif type == 'PUT' :
				response = requests.put(url, json=data)								

			elif type == 'GET' :
				response = requests.get(url, json=data)

		except RequestException as e:
			l.get().w.error("Commander request_processor exception  : {}".format(str(e)))			

		return response 


	def add_task(self, category, job_id=None, task=None):
		l.get().w.debug("Commander add_task category: {} job_id : {} task {} ".format(category, job_id, task))

		result = None
		status = 0

		if category == rc.TRACKER_READY :
			if TaskActivity.checkJobsUnderLimit() is True:
				job_id = DbManager.getJobIndex() + 1
				result, status = self.processor(category, job_id, task)
				if result == 0 : 
					result = job_id
					status = 0

			else:
				result = None
				status =  -22
			return result, status				

		elif category == rc.GET_VISUAL_INFO:
			result, status, data = self.processor(category, job_id)
			return result, status, data

		elif category == rc.GET_VISUAL_DATA :
			result, status, data = self.processor(category, job_id, task)
			return result, status, data			

		elif category > rc.TRACKER_READY :
			# in this category, task is job_id
			result, status = self.processor(category, job_id)
			return result, status


		return result, status


	def processor(self, category, job_id, task=None) :
		result = 0 
		status = 0
		l.get().w.debug("Task processor start  cateory {} job_id {}".format(category, job_id))


		if category == rc.TRACKER_READY :
			trackers = TrackerGroup()
			trackers.set(self.msg_q, task['task_id'], job_id)
			print("--------------- created tracker id : ", id(trackers))
			print("--------------- tracker count exists .. : ", len(trackers.trackers))

			result, status = trackers.prepare(task)
			if result == 0 :
				result = trackers.set_calibration()

			if result == 0 :
				DbManager.insert_newcommand(job_id, 0, task['task_id'])
				self.trck_q.store(job_id, trackers)	

		elif category == rc.GET_VISUAL_INFO :
			data = None
			if (DbManager.check_result_table(job_id) == True) :
				result, st, sf, et, ef = DbManager.get_visual_info(job_id)
				if result >= 0 :
					data = { 'start_time' : st.isoformat(),
					'start_frame' : sf,
					'end_time' : et.isoformat(),
					'end_frame' : ef
					}
			else :
				result = -115

			l.get().w.info("GET_VISUAL_INFO return \n result {} status {}  data {} ".format(result, status, data))
			return result, status, json.dumps(data)


		elif category == rc.GET_VISUAL_DATA : 
			data = None
			if (task['type'] == 'heatmap') : 
				l.get().w.debug("Heatmap job_id {} start frame {} end frame {} ".format(job_id, task['start_frame'], task['end_frame']))
				result, data = Visualize.generate_heatmap(job_id, task['start_frame'], task['end_frame'])


			elif (task['type'] == 'player_3d') :
				l.get().w.debug("player_3d job_id {} target frame {} ".format(job_id, task['target_frame']))
				result, data = Visualize.generate_3d_data(job_id, task['target_frame'])


			elif (task['type'] == 'player_2d') :
				l.get().w.debug("player_2d job_id {} target frame {} ".format(job_id, task['target_frame']))
				result, data = Visualize.generate_2d_data(job_id, task['target_frame'])

			return result, status, data

		else :
			if(self.trck_q.checking(job_id)) :
				l.get().w.error("This message callback can't be handled. Target tracker doesn't exist. {}".format(job_id))
				return -101, status

			if category == rc.TRACKER_START :
				trcks = self.trck_q.get_instance(job_id)
				result, status = trcks.start()

			elif category == rc.TRACKER_STOP :
				trcks = self.trck_q.get_instance(job_id)
				result, status = trcks.stop()

			elif category == rc.TRACKER_STATUS :			
				trcks = self.trck_q.get_instance(job_id)
				result, status = trcks.status()

			elif category == rc.TRACKER_DESTROY :
				trcks = self.trck_q.get_instance(job_id)
				result, status = trcks.destroy()
				self.trck_q.remove(job_id)


		l.get().w.debug("Task processor end result {} status {} ".format(result, status))		
		return result, status

	
	def msg_callback(self, type, job_id, camera_id, data) :
		l.get().w.debug("Commander msg_callback processor  type {} job_id {} camera_id {} ".format(type, job_id, camera_id))				

		if(self.trck_q.checking(job_id)) :
			l.get().w.error("This message callback can't be handled. Target tracker was disappeared. {}".format(job_id))
			return

		trcks = self.trck_q.get_instance(job_id)

		for trck in trcks.trackers : 
			if trck.camera_id == camera_id :
				trck.err_code = data['error_code']
				trck.err_msg = data['error_msg']

				if type == 'setinfo':					
					if trck.err_code == 2000:
						self.step = 'READY_OK'
					else :
						trck.step = 'READY_FAIL'						
					break
				elif type == 'start' :
					if trck.err_code == 2000:
						trck.step = 'START_OK'
						trcks.rabbit.start()
					else :
						trck.step = 'START_FAIL'						
					break

				elif type == 'stop' :
					if trck.err_code == 2000:
						trck.step = 'STOP_OK'
						trcks.rabbit.stop()
					else :
						trck.step = 'STOP_FAIL'
					break
				elif type == 'status' :
					trck.status = data['status']
					break

		#debugging..
		for trck in trcks.trackers : 
			if trck.camera_id == camera_id :
				l.get().w.debug("Tracker camera_id {} -> err_code {} step {} ".format(
					trck.camera_id, trck.err_code, trck.step))

				
