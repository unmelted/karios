import os
import enum

VERSION = 'V0.0.0.1'

class RequestCategory :
	INIT = 0
	GET_VERSION = 10
	TRACKER_READY = 100
	TRACKER_RUN = 200
	TRACKER_STOP = 300
	TRACKER_FINISH = 400
	SIMULATION_START = 500
	SIMULATION_STOP = 600
	

class Definition(object) : 
	
	BOT_TOKEN = '5578949849:AAEJHteVLGJnydip3x5eYwJQQgcPymWGu4s'
	CHAT_ID = '1140943041'  # '5623435982'

	def get_version(self):
		return VERSION

def get_err_msg(err_code) :

	msg = None
	msg_pair = {
		0 : "ERR_NONE",
		100 : "Complete",

		-1 : "PROC_ERR"
	}

	if err_code in msg_pair :
		msg = msg_pair[err_code]
	else :
		msg = 'None'

	return msg