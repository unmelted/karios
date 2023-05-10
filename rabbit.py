import os
import time
import json
import pika
import socket

class Consumer() :

	ip_addr = None
	queue_port = 5672
	queue_name = None
	channel = None

	def __init__(self, job_id):
		self.job_id = str(job_id)
		self.queue_name = 'karios_'+ self.job_id
		self.credentials = pika.PlainCredentials('replay', '1234')		
		self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', self.queue_port, '/', self.credentials))
		self.channel = self.connection.channel()
		self.channel.queue_declare(queue=self.queue_name, durable=True, auto_delete=True)
		self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
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
		print("My ip address is : ", self.ip_addr)

	def callback(self, method, properties, body) :
		print("received message : ", body)
		self.channel.basic_ack(delivery_tag=method.delivery_tag)

	# def consume(self) :
		self.channel.start_consuming()
	
	def close(self) :
		self.channel.queue_delete(self.job_id)
		self.channel.close()
