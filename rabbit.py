import os
import time
import json
import pika

class Consumer() :

	def __init__(self, job_id):
		job_id = str(job_id)
		credentials = pika.PlainCredentials('replay', '1234')		
		connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', credentials))
		channel = connection.channel()
		channel.queue_declare(queue=job_id, durable=True, auto_delete=True)
		channel.basic_consume(queue=job_id, on_message_callback=self.callback)
	
	def callback(self, method, properties, body) :
		print("received message : ", body)
		self.channel.basic_ack(delivery_tag=method.delivery_tag)

	def consume(self) :
		self.channel.start_consuming()
	
	def close(self) :
		self.channel.queue_delete(self.job_id)
		self.channel.close()
