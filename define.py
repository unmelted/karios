import os
import enum

VERSION = 'V0.0.0.1'

class RequestCategory :
	INIT = 0
	GET_VERSION = 10
	TRACKER_READY = 100
	TRACKER_START = 200
	TRACKER_STOP = 300
	TRACKER_DESTROY = 400
	SIMULATION_START = 500
	SIMULATION_STOP = 600
	TRACKER_STATUS = 700

class Definition(object) : 
	
	BOT_TOKEN = '5578949849:AAEJHteVLGJnydip3x5eYwJQQgcPymWGu4s'
	CHAT_ID = '1140943041'  # '5623435982'
	base_index = 100
	task_limit = 5	

	tracker_name = '/kronos'
	tracker_port = 7890

	backend_url = '10.82.5.119'
	backend_port = 4000

	prefix = 'kairos_'

	exodus_ip = '10.82.5.130'
	exodus_port = 9000
	exodus_cmd = '/exodus/autocalib/'

	shared_dir = '/mnt/images/' # local env only

	def get_version(self):
		return VERSION

def get_err_msg(err_code) :

	msg = None
	msg_pair = {
        0: "ERR NONE",
        100: "Complete",
        200: "Complete",

        -1: "PROC ERR",
        -11: "Create Preset Error",
        -12: "Can not open and read pts file",
        -13: "Image count is not match with dsc_id in pts",
        -21: "Input value is invalid",
        -22: "Can not add task. Now I'm busy..",
        -23: "Acess Denied to System Process",
        -24: "There is image file problem - Upload again",
        -25: "Canceled Job",

		-101: "There is no prepared Multitracker Job",
		-102: "Not all tracker is ready. Partially started.",
		-103: "Can't stop some trackers.",
		-104: "There is no stop-able trackers.",
		-105: "There is no ready trackers",
		-106: "Insufficient values for initialize TrackerGroup.",
		-107: "There tracker set has no calibration data.",
		-108: " No pts file for calibration.",
		-109: "Can't open the pts file",
		-110: "Send request to Exodus, but response is error",
		-111: "Can't find matched calibration data. (calib type data)",
		-112: "Can't find matched calibration data. (camera name match)",

		-201: "Some Exception Error is occurred during requests.",
		-202: "No process exception is occurred during Multiprocessor destroy.",
		-203: "AccessDenied exception is occurred during Multiprocessor destroy."

	}

	if err_code in msg_pair :
		msg = msg_pair[err_code]
	else :
		msg = 'None'

	return msg