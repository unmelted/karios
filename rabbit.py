import os
import time
import json
import pika
import socket
import threading

from logger import Logger as l
from define import Definition as defn
from db_manager import DbManager


class MQConnection():

	queue_name = None

	def __init__(self, parameters, queue_name, table_name):
		self.parameter = parameters
		self.connection = None
		self.channel = None
		self.queue_name = queue_name
		self.table_name = table_name


	def ready(self):
		self.connection = pika.BlockingConnection(parameters=self.parameter)
		self.channel = self.connection.channel()
		self.channel.queue_declare(queue=self.queue_name, durable=True, auto_delete=True)
		self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.on_message)		

	def start(self)	:
		self.channel.start_consuming()

	def stop(self):
		self.channel.stop_consuming()

	def on_message(self, channel, method, properties, body):
		print("Received message:", properties)
		json_body = json.loads(body)
		print(json_body)
		print(type(json_body))
		# json_prop = json.loads(properties.headers)
		# print(properties.headers)
		# print(properties.headers['from_id'])
		DbManager.insert_que_result(self.table_name, 
									properties.headers['frame_id'], 
									properties.headers['camera_id'],
									properties.headers['from_id'],
									json_body['objects'])

		self.channel.basic_ack(delivery_tag=method.delivery_tag)

	def close(self):
		self.channel.queue_delete(self.job_id)
		self.channel.close()
	


class Consumer() :

	param = None
	connection = None
	ip_addr = None
	queue_port = 5672
	channel = None

	thread_producer = None
	threahd_consumer = None

	run_flag = True

	def __init__(self, job_id):
		self.job_id = str(job_id)		
		self.queue_name = defn.prefix + self.job_id
		self.table_name1 = defn.prefix+ self.job_id + '_result'		
		self.credentials = pika.PlainCredentials('replay', '1234')		

		self.param = pika.ConnectionParameters('localhost', self.queue_port, '/', self.credentials)
		self.mq = MQConnection(self.param, self.queue_name, self.table_name1)
		self.mq.ready()
		self.getIpAddress()


	def getQueName(self) :
		return self.queue_name

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
		print("rabbit mq receive consume start..")
		self.thread_consumer = threading.Thread(target=self.mq.start)
		self.thread_consumer.start()
		# # time.sleep(1)		
		# self.produce_msg()
	
	def stop(self) :
		if self.thread_producer != None :
			self.run_flag = False
			self.thread_producer.join()

		if self.thread_consumer != None :
			self.mq.stop()


	def close(self) :
		self.mq.close()		
		# self.thread_consumer.join()

	def produce_msg(self) :
		print("produce msage start... ")

		def sample_msg(que_name, run_flag) :
			cam_index = '101101'
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

				msgs = [{ "id" : 10, "x": 0.0526, "y": 0.125, "width": 0.1875, "height": 0.427, "conf" : 0.0, "team" : 'None'}, { "id" : 20, "x": 0.0626, "y": 0.4, "width": 0.33, "height": 0.31, "conf" : 0.0, "team" : 'None'}]

				json_msg = json.dumps(msgs)
				print(json_msg)
				frame_id += 2
				channel.basic_publish(exchange='', routing_key=que_name, properties=properties, body=json_msg)

		q_name = str(self.queue_name) 
		print("str name : " , q_name)

		self.thread_producer = threading.Thread(target=sample_msg, args=(q_name, self.run_flag))
		self.thread_producer.start()


