import os
import enum

VERSION = 'V0.0.0.1'

class RequestCategory :
	## multi-channel tracker job	
	GET_VERSION = 10
	TRACKER_READY = 100
	TRACKER_START = 200
	TRACKER_STOP = 300
	TRACKER_DESTROY = 400
	TRACKER_STATUS = 700
	GET_VISUAL_INFO = 800
	GET_VISUAL_DATA = 900		

	##pose estimation job
	LOAD_POSE_MODEL = 1000
	ESTIMATE_POSE = 1100
	DETECT_BALL = 1200



class Definition(object) : 
	
	BOT_TOKEN = '5578949849:AAEJHteVLGJnydip3x5eYwJQQgcPymWGu4s'
	CHAT_ID = '1140943041'  # '5623435982'
	base_index = 100
	task_limit = 5	

	## kairos - multichannel tracker
	tracker_name = '/kronos'
	tracker_port = 7890

	backend_url = '10.82.5.119'
	backend_port = 4000

	visualize_data_limit = 100000
	horizontal_grid = 50
	vertical_grid = 28

	def get_que_name(job_id) :
		prefix = 'kairos_'		
		return prefix + str(job_id)

	def get_table_name(job_id) :
		prefix = 'kairos_'		
		return prefix + str(job_id)	+ '_2d', prefix + str(job_id) + '_3d'

	## kairos - mct end

	## kairos 
	pose_path = 'pose_models/ViTPose'
	pose_config = os.path.join(pose_path, 'configs/body/2d_kpt_sview_rgb_img/associative_embedding/coco/hrnet_w32_coco_512x512.py')
	pose_checkpoint = os.path.join( pose_path, 'model/hrnet_w32_coco_512x512-bcb8c247_20200816.pth')
	pose_nms_thr = 0.9
	pose_dump = 'dump/'
	pose_keypoint_thr = 0.3 #keypoint score threshold
	pose_visualize_radius = 4
	pose_visualuze_thick = 1


	exodus_ip = '10.82.5.130'
	exodus_port = 9000
	exodus_cmd = '/exodus/autocalib/'
	shared_dir = '/mnt/images/' # local env only


	def get_version():
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
		-112: "Can't find matched calibration data. (camera name or group match)",
		-113: "Prepare Fail. Some cameras can't get calibration data.",
		-114 : "Find homography can't be calculated.",
		-115 : "Can't find result table of tracker group.",
		-116 : "Cant' get the visualize info from result table. (DB Error)",
		-117 : "Visualize type is wrong.",
		-118 : "Result is empty for Visualizing.", 
		-119 : "Result is too much. Decrease the range.",

		-201: "Some Exception Error is occurred during requests.",
		-202: "No process exception is occurred during Multiprocessor destroy.",
		-203: "AccessDenied exception is occurred during Multiprocessor destroy."

	}

	if err_code in msg_pair :
		msg = msg_pair[err_code]
	else :
		msg = 'None'

	return msg