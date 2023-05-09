import os
import time
import json

from define import Definition as defn
from utility import *


class Tracker() :

	tracker_ip = None
	tracker_port = defn.tracker_port
	tracker_name = defn.tracker_name

	camera_id = None
	stream_url = None

	status = None
	group = None

	def __init__ (self, tracker_ip, camera_id, stream_url) :
		self.tracker_ip = tracker_ip
		self.camera_id = camera_id
		self.stream_url = stream_url
		self.send_url = 'http://'+self.tracker_ip+ ':'+ str(self.tracker_port) + self.tracker_name

class MultiTracker() :

	msg_que = None
	job_id = None
	trackers = []
#	url = 'http://10.82.5.148:7890/kronos/setinfo'
	def __init__ (self, que):
		self.msg_que = que

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
			print("returned message " , msg)			
			self.msg_que.put((setinfo_url, msg))

		print("prepare end : " , self.trackers)


