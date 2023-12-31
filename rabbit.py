import os
import psutil
import multiprocessing
import time
import json
import pika
import socket
import threading
import numpy as np
import cv2

from logger import Logger as l
from define import Definition as defn
from db_manager import DbManager


class MQConnection():

	queue_name = None
	Hset = None		

	def __init__(self, parameters, queue_name, table_name1, table_name2):
		self.parameter = parameters
		self.connection = None
		self.channel = None
		self.queue_name = queue_name
		self.table_name1 = table_name1
		self.table_name2 = table_name2		


	def ready(self):
		self.connection = pika.BlockingConnection(parameters=self.parameter)
		self.channel = self.connection.channel()
		self.channel.queue_declare(queue=self.queue_name, durable=True, auto_delete=True)
		self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.on_message)		

	def start(self)	:
		self.channel.start_consuming()

	def stop(self):		
		self.channel.stop_consuming()

	def close(self):
		self.channel.queue_delete(self.queue_name)
		self.channel.close()

	def on_message(self, channel, method, properties, body):
		print("Received message:", properties)
		json_body = json.loads(body)
		print(json_body)
		# print(type(json_body ))
		# print(properties.headers)
		# print(properties.headers['from_id'])
		self.convert_message_body(properties, json_body)
		self.channel.basic_ack(delivery_tag=method.delivery_tag)

	def convert_message_body(self, properties, body) :
		# print(self.Hset[properties.headers['camera_id']])
		H = self.Hset[properties.headers['camera_id']]

		for obj in body['objects'] :
			DbManager.insert_que_result_2d(self.table_name1,
						properties.headers['frame_id'], 
						properties.headers['camera_id'],
						obj)

			pt = np.float32(np.array( [[[ obj['x'], obj['y'] ]]]))
			mv_pt = cv2.perspectiveTransform(pt, H)
			print("moved pt " , mv_pt)

			obj['x'] = mv_pt[0][0][0]
			obj['y'] = mv_pt[0][0][1]
	
			DbManager.insert_que_result_3d(self.table_name2, 
									properties.headers['frame_id'], 
									properties.headers['camera_id'],
									properties.headers['from_id'],
									obj)
		
	


class Consumer() :

	param = None
	connection = None
	ip_addr = None
	queue_port = 5672
	channel = None
	consumer_count = 0

	thread_producer = None
	mqs = []
	consumers = []

	run_flag = True

	def __init__(self, job_id, count):
		self.job_id = str(job_id)
		self.consumer_count = count

		self.queue_name = defn.get_que_name(self.job_id)
		self.table_name1, self.table_name2 = defn.get_table_name(self.job_id)
		self.credentials = pika.PlainCredentials('replay', '1234')		

		self.param = pika.ConnectionParameters('localhost', self.queue_port, '/', self.credentials)
		mq = MQConnection(self.param, self.queue_name, self.table_name1, self.table_name2)
		mq.ready()
		self.mqs.append(mq)

		self.getIpAddress()


	def getQueName(self) :
		return self.queue_name
	
	def set_Hset(self, hset) :

		for mq in self.mqs : 
			mq.Hset = hset

	def getResultQueInfo(self) :
		result_q = {"result_send_info": {
			"ip": self.ip_addr,
			"port": self.queue_port,
			"queue": self.queue_name
		}}

		print("getResult que info : ", result_q)
		return result_q

	def getIpAddress(self) :
		hostname = socket.gethostname()
		self.ip_addr = socket.gethostbyname(hostname)


	def start(self) :

		print("rabbit mq receive consume start . create processing : ", self.consumer_count)
		for i in range(self.consumer_count) :
			consumer = multiprocessing.Process(target=self.mqs[i].start)
			consumer.start()			
			self.consumers.append(consumer)

		#threading method
		# self.thread_consumer = threading.Thread(target=self.mq.start)
		# self.thread_consumer.start()

		# time.sleep(1) # if you want self producing, enalbe this.
		# self.produce_msg()
	
	def stop(self) :
		if self.thread_producer != None :
			self.run_flag = False
			self.thread_producer.join()


	def close(self) :
		result = 0
		status = 0

		for mq in self.mqs :
			mq.stop()
			mq.close()
			print("Rabbit close function in loop ..")

		# self.thread_consumer.join()
		print("rabbit close is called ")
		for consumer in self.consumers :
			print("stop consumer processing ------  ", consumer)
			try : 
				consumer.terminate()
				print("terminate ok")

			except psutil.NoSuchProcess :
				print("psutil.NoSuchProcess ")
				result = -202

			except psutil.AccessDenied :
				print("psutil.AccessDenied ")
				result = -203				

		return result, status



	def produce_msg(self) :
		print("produce msage start... ")

		def sample_msg(que_name, run_flag) :
			cam_index = '001014'
			frame_id = 10000
			print("sample_msg : ", que_name)

			credentials = pika.PlainCredentials('replay', '1234')
			param = pika.ConnectionParameters('localhost', 5672, '/', credentials)			
			connection = pika.BlockingConnection(param)
			channel = connection.channel()

			while run_flag :
				time.sleep(0.5)
				print("-")

				headers = {"content-type" : "application/json"}
				custom_headers = {"from_id" : "10.82.5.148", "camera_id" : cam_index, "frame_id" :frame_id}
				properties = pika.BasicProperties(headers=custom_headers)

				msgs = {"objects" : [{ "id" : 10, "x": 0.0526, "y": 0.125, "width": 0.1875, "height": 0.427, "conf" : 0.0, "team" : 'None'}, { "id" : 20, "x": 0.0626, "y": 0.4, "width": 0.33, "height": 0.31, "conf" : 0.0, "team" : 'None'}]}

				json_msg = json.dumps(msgs)
				# print(json_msg)
				frame_id += 2
				channel.basic_publish(exchange='', routing_key=que_name, properties=properties, body=json_msg)

		q_name = str(self.queue_name) 
		print("str name : " , q_name)

		self.thread_producer = threading.Thread(target=sample_msg, args=(q_name, self.run_flag))
		self.thread_producer.start()


