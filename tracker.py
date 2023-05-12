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

		return url
	
	# def callback(self, url, data) :
	# 	print(" Tracker Callback is called  ", url)
	# 	print(self)

	# 	if url == self.getUrl('setinfo') :
	# 		if data['status'] == 'ready': 
	# 			self.step = 'READY_OK'				
	# 			print("target tracker cam id : " , self.camera_id)
	# 			self.camera_id = 'TEST_ID'
	# 		else : 
	# 			self.step = 'READY_FAIL'

	# 	elif url == selfg.getUrl('start') :
	# 		if data['status'] == 'start': 			
	# 			self.step = 'START_OK'
	# 		else :
	# 			self.step = 'START_FAIL'

	# 	elif url == self.getUrl('stop') :
	# 		print("stop callback .. ", data)			
	# 		if data['status'] == 'stop':
	# 			self.step = 'STOP_OK'
	# 		else :
	# 			self.step = 'STOP_FAIL'

	# 	self.err_code = data['error_code']
	# 	self.err_msg = data['error_msg']				
	# 	print("changed step : ", self.step, self.camera_id)
	# 	print(self)


class TrackerGroup() :

	msg_que = None
	job_id = None
	task_id = None
	trackers = []
	rabbit = None

	def __init__ (self, que, task_id, job_id):
		self.task_id = task_id
		self.job_id = job_id
		self.msg_que = que
		self.rabbit = Consumer(job_id)

	
	def prepare(self, task) :

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
				self.msg_que.put((tr.getUrl('start'), 'PUT', none, tr.callback))
				start_cnt += 1
			else :
				status = -102

		if start_cnt == 0 and status == -102 :
			status = -101
		
		print("start return ", result, status)
		return result, status

	def stop(self) :
		result = 0
		status = 0
		stop_cnt = 0
		for tracker in self.trackers :
			if tracker.step == 'START_OK' : 
				self.msg_que.put((tr.getUrl('stop'), 'PUT', none, tr.callback))
				stop_cnt += 1
			else :
				status = -103

			if stop_cnt == 0 and status == -103:
				status = -101	

		return result, status

	def status(self) :
		print("Tracker Group status check is called ")
		result = 0
		status = 0

		for tracker in self.tracker :
			if tracker.step == 'START_OK' :
				self.msg_que.put((tr.getUrl('start'), 'GET', none, tr.callback))

		return result, status