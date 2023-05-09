import os
import time
import json
from enum import Enum

from define import Definition as defn
from utility import *
from rabbit import Consumer


class Tracker() :
	class LIFECYCLE_DEF(Enum) :
		CREATED = 100
		READY_OK = 200
		READY_FAIL = 300
		RUN = 400
		STOP = 500


	tracker_ip = None
	tracker_port = defn.tracker_port
	tracker_name = defn.tracker_name

	camera_id = None
	stream_url = None

	lifecycle = None
	status = None
	group = None


	def __init__ (self, tracker_ip, camera_id, stream_url) :
		self.lifecycle = self.LIFECYCLE_DEF.CREATED
		self.tracker_ip = tracker_ip
		self.camera_id = camera_id
		self.stream_url = stream_url
		self.send_url = 'http://'+self.tracker_ip+ ':'+ str(self.tracker_port) + self.tracker_name

	def callback(self, data) :
		print("tracker handler setinfo after : ", data)	

		if (self.lifecycle == self.LIFECYCLE_DEF.CREATED) :
			if (data['ret'] == 'ok') :
				self.lifecycle = self.LIFECYCLE_DEF.READY_OK
			else :
				self.lifecycle = self.LIFECYCLE_DEF.READY_FAIL				
			print("now my lifecycle : ", self.lifecycle)

class MultiTracker() :

	msg_que = None
	job_id = None
	trackers = []
	rabbit = None

	def __init__ (self, que, job_id):
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

			setinfo_url = tr.send_url + '/setinfo'
			msg = Messages.assemble_info_msg('setinfo', tr)
			# print("returned message " , msg)			
			self.msg_que.put((setinfo_url, msg, tr.callback))

		print("prepare end : " , self.trackers)


