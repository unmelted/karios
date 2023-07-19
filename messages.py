import os
import time
import json

class Messages() :

	jfile = open(os.path.join(os.getcwd(), 'util', 'handle_message.json'), 'r')
	messages = json.load(jfile)

	@classmethod
	def assemble_info_msg(cls, type, data):

		if type == 'setinfo' :
			msg = cls.messages['setinfo']
			msg['camera_id'] = data[0].camera_id
			msg['stream_url'] = data[0].stream_url
			msg['result_send_info'] = data[1]['result_send_info']

		return msg

