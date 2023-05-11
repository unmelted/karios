import os
import time
import json
from enum import Enum

from define import Definition as defn
from utility import *
from rabbit import Consumer
from db_manager import DbManager


class Tracker() :
	class LIFECYCLE_DEF(Enum) :
		CREATED = 100
		READY_OK = 200
		READY_FAIL = 300
		START_OK = 400
		START_FAIL = 500
		STOP_OK = 500
		STOP_FAIL = 600


	tracker_ip = None
	tracker_port = defn.tracker_port
	tracker_name = defn.tracker_name

	camera_id = None
	stream_url = None

	lifecycle = None
	status = None
	err_code = None
	err_msg = None
	group = None


	def __init__ (self, tracker_ip, camera_id, stream_url) :
		self.lifecycle = self.LIFECYCLE_DEF.CREATED
		self.tracker_ip = tracker_ip
		self.camera_id = camera_id
		self.stream_url = stream_url
		self.send_url = 'http://'+self.tracker_ip+ ':'+ str(self.tracker_port) + self.tracker_name

	def callback(self, data) :
		print("tracker handler setinfo after : ", data)	
		print("current lifecycle : ", self.lifecycle)

		if (self.lifecycle == self.LIFECYCLE_DEF.CREATED) :
			if (data['status'] == 'ready') :
				self.lifecycle = self.LIFECYCLE_DEF.READY_OK
			else :
				self.lifecycle = self.LIFECYCLE_DEF.READY_FAIL


		elif (self.lifecycle == self.LIFECYCLE_DEF.READY_OK) :
			if (data['status'] == 'start') :
				self.lifecycle = self.LIFECYCLE_DEF.START_OK
			else :
				self.lifecycle = self.LIFECYCLE_DEF.START_FAIL				

		elif (self.lifecycle == self.LIFECYCLE_DEF.START_OK) :
			if (data['status'] == 'stop') :
				self.lifecycle = self.LIFECYCLE_DEF.STOP_OK
			else :
				self.lifecycle = self.LIFECYCLE_DEF.STOP_FAIL

		self.err_code = data['error_code']
		self.err_msg = data['error_msg']				
		print("changed lifecycle : ", self.lifecycle)

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


			tr = Tracker( mobj['tracker_ip'], mobj['camera_id'], mobj['stream_url'])
			print("created tracker : ", tr.tracker_ip, tr.stream_url)

			self.trackers.append(tr)
			DbManager.insert_tracker_info(self.job_id, tr.tracker_ip, tr.stream_url)

			setinfo_url = tr.send_url + '/setinfo'
			msg = Messages.assemble_info_msg('setinfo', (tr, self.rabbit.getResultQueInfo()))
			self.msg_que.put((setinfo_url, msg, tr.callback))

		print("prepare end : " , self.trackers)


	def start(self) :
		print("Tracker Group start is called.. ")

		for tracker in self.trackers :
			if tracker.lifecycle == tracker.LIFECYCLE_DEF.READY_OK :
				start_url = tracker.send_url + '/start'
				self.msg_que.put((start_url, none, tr.callback))

	def stop(self) :
		for tracker in self.trackers :
			stop_url = tracker.send_url + '/stop'
			self.msg_que.put((stop_url, none, tr.callback))


