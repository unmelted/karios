import os
import time
import json
import threading
from enum import Enum

from define import Definition as defn
from utility import *
from rabbit import Consumer
from db_manager import DbManager


class Tracker() :
	'''
		CREATED = 100
		READY_OK = 200
		READY_FAIL = 300
		START_OK = 400
		START_FAIL = 500
		STOP_OK = 500
		STOP_FAIL = 600
	'''
	step = ''
	status = None
	err_code = None
	err_msg = None
	group = None

	tracker_ip = None
	tracker_port = defn.tracker_port
	tracker_name = defn.tracker_name

	camera_id = None
	stream_url = None
	send_url = None
	calib_job_id = None


	def set_data(self, tracker_ip, camera_id, stream_url) :
		print("tracker () set is called () ")
		self.step = 'CREATED'
		self.tracker_ip = tracker_ip
		self.camera_id = camera_id
		self.stream_url = stream_url
		self.send_url = 'http://'+self.tracker_ip+ ':'+ str(self.tracker_port) + self.tracker_name
		print("my --------- ", self.send_url)

	def getUrl(self, type) :
		url = None
		print("get url --- ", self.send_url)
		if type == 'setinfo' :
			url = self.send_url + '/setinfo'
		elif type == 'start' :
			url = self.send_url + '/start'
		elif type == 'stop' :
			url = self.send_url + '/stop'
		elif type == 'status' :
			url = self.send_url + '/status'

		return url
	

class TrackerGroup() :

	msg_que = None
	job_id = None
	task_id = None
	trackers = []
	rabbit = None
	table_name1 = None
	table_name2 = None

	def __init__ (self, que, task_id, job_id):
		print(" ################  trackerGroup init is called ")		
		self.task_id = task_id
		self.job_id = job_id
		self.msg_que = que
		self.table_name1 = defn.prefix+ str(self.job_id)
		self.table_name2 = defn.prefix+ str(self.job_id) + '_3d'

	
	def prepare(self, task) :

		self.rabbit = Consumer(self.job_id, len(task['tracker']))
		
		for tracker in task['tracker']:
			print("prepare for eache : ", tracker)
			obj = tracker.replace('\'', '\"')
			mobj = json.loads(obj)


			tr = Tracker()
			tr.set_data( mobj['tracker_ip'], mobj['camera_id'], mobj['stream_url'])
			print("created tracker : ", tr.tracker_ip, tr.stream_url)
			print(tr)
			self.trackers.append(tr)
			DbManager.insert_tracker_info(self.job_id, tr.tracker_ip, tr.stream_url)
			DbManager.create_result_table(self.table_name1, self.table_name2)

			msg = Messages.assemble_info_msg('setinfo', (tr, self.rabbit.getResultQueInfo()))
			self.msg_que.put((tr.getUrl('setinfo'), 'POST', msg, 'setinfo', self.job_id, tr.camera_id))

		print("prepare end : " , self.trackers)



	def start(self) :
		print("Tracker Group start is called.. ")
		result = 0
		status = 0
		start_cnt = 0
		for tracker in self.trackers :
			print("inner for tracker ... ", tracker.step)
			print(tracker.camera_id)
			print(tracker.tracker_ip)
			print(tracker.stream_url)

			if tracker.step == 'READY_OK' :
				self.msg_que.put((tracker.getUrl('start'), 'PUT', None, 'start', self.job_id, tracker.camera_id))
				start_cnt += 1
			else :
				status = -102

		if start_cnt == 0 and status == -102 :
			status = -105
		
		print("start return ", result, status)
		return result, status

	def stop(self) :
		result = 0
		status = 0
		stop_cnt = 0
		for tracker in self.trackers :
			if tracker.step == 'START_OK' : 
				self.msg_que.put((tracker.getUrl('stop'), 'PUT', None, 'stop', self.job_id, tracker.camera_id))
				stop_cnt += 1
			else :
				status = -103

			if stop_cnt == 0 and status == -103:
				status = -104

		return result, status

	def status(self) :
		print("Tracker Group status check is called ")
		result = 0
		status = 0

		for tracker in self.tracker :
			self.msg_que.put((tr.getUrl('status'), 'GET', None, 'status', self.job_id, tracker.camera_id))

		return result, status