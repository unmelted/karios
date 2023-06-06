import os
import time
import json
import threading
from enum import Enum
import numpy as np

from logger import Logger as l
from define import Definition as defn
from messages import *
from rabbit import Consumer
from db_manager import DbManager
from calib import Calibration

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

	def __init__(self) :
		self.step = ''
		self.status = None
		self.err_code = None
		self.err_msg = None
		self.group = None

		self.tracker_ip = None
		self.tracker_port = defn.tracker_port
		self.tracker_name = defn.tracker_name

		self.camera_id = None
		self.stream_url = None
		self.send_url = None
		self.calib_job_id = None

		self.world_pts = None
		self.pts_3d = None

	
	def set_data(self, group, tracker_ip, camera_id, stream_url, calib_job_id) :

		self.step = 'CREATED'
		self.group = group
		self.tracker_ip = tracker_ip
		self.camera_id = camera_id
		self.stream_url = stream_url
		self.send_url = 'http://'+self.tracker_ip+ ':'+ str(self.tracker_port) + self.tracker_name
		self.calib_job_id = calib_job_id

		l.get().w.debug("Tracker set data ip {} stream_url {} calib_job_id {} ".format(
			self.tracker_ip, self.stream_url, self.calib_job_id))

	def getUrl(self, type) :
		url = None

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

	def __init__(self):

		self.msg_que = None
		self.job_id = None
		self.task_id = None
		self.trackers = []  # Initialize as an instance variable
		self.rabbit = None
		self.table_name1 = None
		self.table_name2 = None
		self.calib_id = []
		self.calib = None
		self.Hset = {}

	def set(self, que, task_id, job_id):

		self.task_id = task_id
		self.job_id = job_id
		self.msg_que = que
		self.table_name1 = defn.prefix+ str(self.job_id)
		self.table_name2 = defn.prefix+ str(self.job_id) + '_3d'

	
	def prepare(self, task) :
		result, status = 0, 0
		self.rabbit = Consumer(self.job_id, len(task['tracker']))
		cal_id = []

		for tracker in task['tracker']:

			obj = tracker.replace('\'', '\"')
			mobj = json.loads(obj)
			print("Tracker add ", mobj)

			tr = Tracker()
			if mobj['tracker_ip'] != '' and  mobj['camera_id'] != '' and  mobj['stream_url'] != '' and mobj['calib_job_id'] != '':
				tr.set_data( mobj['group'], mobj['tracker_ip'], mobj['camera_id'], mobj['stream_url'], mobj['calib_job_id'])
				cal_id.append(mobj['calib_job_id'])
				self.trackers.append(tr)

				msg = Messages.assemble_info_msg('setinfo', (tr, self.rabbit.getResultQueInfo()))
				self.msg_que.put((tr.getUrl('setinfo'), 'POST', msg, 'setinfo', self.job_id, tr.camera_id))

			else : 
				result = -106

		if ( task['calib_type'] == 'exodus') :
			if len(cal_id) > 0 :
				self.calib_id = list(set(cal_id));
			else : 
				result = -107
			
		elif ( task['calib_type'] == 'file') :
			if ( task['calib_file'] == '' ) :
				result = -108

		if( result == 0 ) :
			DbManager.create_result_table(self.table_name1, self.table_name2)			
			self.calib = Calibration(task['calib_type'], task['calib_file'], self.calib_id)

		l.get().w.debug("TrackerGourp Prepare End. result {} ".format(result))
		return result, status 


	def set_calibration(self) :

		result = self.calib.load_data()
		if result < 0 :
			return result

		bfail = False
		print("set_calibration.. tracker count : ", len(self.trackers))

		for tracker in self.trackers :
			print(tracker.camera_id, tracker.tracker_ip, tracker.stream_url)
			result, tracker.world_pts, tracker.pts_3d = self.calib.get_points(tracker.camera_id, tracker.group, tracker.calib_job_id)
			l.get().w.debug("Tracker set calibration data camera {} ---  world {} pts_3d {} result {} ".format(tracker.camera_id, tracker.world_pts, tracker.pts_3d, result))

			if result == 0 :
				result, H = self.calib.get_homography(tracker.world_pts, tracker.pts_3d)
				if result == 0 :
					self.Hset[tracker.camera_id] = H
	
			tracker.err_code = result
			if result == 0 :
				tracker.step = 'READY_OK'
				DbManager.insert_tracker_info(self.job_id, tracker.tracker_ip, tracker.stream_url)				
			else :
				tracker.step = 'READY_FAIL'
				bfail = True

		if bfail == True :
			result = -113
		else :
			self.rabbit.set_Hset(self.Hset)

		return result


	def start(self) :

		result = 0
		status = 0
		start_cnt = 0
		for tracker in self.trackers :

			if tracker.step == 'READY_OK' :
				self.msg_que.put((tracker.getUrl('start'), 'PUT', None, 'start', self.job_id, tracker.camera_id))
				start_cnt += 1
			else :
				status = -102

		if start_cnt == 0 and status == -102 :
			status = -105
		
		l.get().w.debug("TrackerGourp Start result {} status {}. ".format(result, status))		
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

		l.get().w.debug("TrackerGourp Stop result {} status {}. ".format(result, status))		
		return result, status

	def destroy(self) :
		result = 0
		status = 0

		result, status = self.rabbit.close()

		for tracker in self.trackers : 
			self.trackers.remove(tracker)

		l.get().w.debug("TrackerGourp Destroy result {} status {}. ".format(result, status))
		return result, status 


	def status(self) :
		result = 0
		status = 0

		for tracker in self.trackers :
			self.msg_que.put((tr.getUrl('status'), 'GET', None, 'status', self.job_id, tracker.camera_id))

		l.get().w.debug("TrackerGourp Status request send.")
		return result, status