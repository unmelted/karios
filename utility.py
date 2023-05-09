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
			msg['camera_id'] = data.camera_id
			msg['stream_url'] = data.stream_url

		return msg

