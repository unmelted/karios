import os

from multiprocessing import Process, Queue, Manager
from flask import Flask
from flask import request, jsonify
from flask_restx import fields, Resource, Api, reqparse, marshal

import define  as defn
from define import RequestCategory as rc
from task import TaskManager
from db_layer import NewPool, DBLayer
from command import *


app = Flask(__name__)
api = Api(app, version='0.1', title='KAIROS')
app.config.SWAGGER_UI_DOC_EXPANSION = 'full'

ready_info = api.model('ready_info', {
    'task_id' : fields.String,
    'calib_type' : fields.String,
    'calib_file' : fields.String,
    'tracker' : fields.List(fields.Raw({ "type" : "String"}, io = 'r'))
})


@api.route('/kairos/mct/ready')
@api.doc()
class ready(Resource):
    @api.expect(ready_info)
    def post(self, model=ready_info):

        parser = reqparse.RequestParser()
        parser.add_argument('task_id', type=str)
        parser.add_argument('calib_type', type=str)
        parser.add_argument('calib_file', type=str)
        parser.add_argument('tracker', default=list, action='append')
        args = parser.parse_args()
        print('ready command args : ', args)

        result, status = Commander().add_task(rc.TRACKER_READY, None, args)
        msg = defn.get_err_msg(result)
        result = {
            'status': status,
            'job_id': result,
            'message': msg,
        }

        return result

job_id = api.model('job_id', {
    'job_id': fields.String,
})

@api.route('/kairos/mct/start/<job_id>')
@api.doc()
class Start(Resource) :
    def put(self, job_id=job_id):
        print("start receive.. job_id : ", job_id)
        result, status = Commander().add_task(rc.TRACKER_START, job_id)
        msg = defn.get_err_msg(result)

        result = {
            'status' : status,
            'result' : result,
            'message' : msg
        }
        print("will return to server : ", status, result)

        return result


@api.route('/kairos/mct/stop/<job_id>')
@api.doc()
class Stop(Resource) :
    def put(self, job_id=job_id):
        
        result, status = Commander().add_task(rc.TRACKER_STOP, job_id)
        msg = defn.get_err_msg(result)

        result = {
            'status' : status,
            'result' : result,
            'message' : msg
        }

        return result
  
@api.route('/kairos/mct/destroy/<job_id>')
@api.doc()
class Destroy(Resource) :
    def put(self, job_id=job_id):
        
        result, status = Commander().add_task(rc.TRACKER_DESTROY, job_id)
        msg = defn.get_err_msg(result)

        result = {
            'status' : status,
            'result' : result,
            'message' : msg
        }

        return result
        
@api.route('/kairos/mct/status/<job_id>')
@api.doc()
class GetStatus(Resource) :
    def get(self, job_id=job_id):

        result, status = Commander().add_task(rc.TRACKER_STATUS, job_id)
        msg = defn.get_err_msg(result)

        result = {
            'status' : status,
            'result' : result,
            'message' : msg
        }

        return result

@api.route('/kairos/mct/destroy/<job_id>')
@api.doc()
class GetStatus(Resource) :
    def put(self, job_id=job_id):

        result, status = Commander().add_task(rc.TRACKER_DESTROY, job_id)
        msg = defn.get_err_msg(result)

        result = {
            'status' : status,
            'result' : result,
            'message' : msg
        }

        return result

@api.route('/kairos/mct/visualinfo/<job_id>')
@api.doc()
class GetVsiaulizeInfo(Resource) :
    def get(self, job_id=job_id):

        result, status, data = Commander().add_task(rc.GET_VISUAL_INFO, job_id)
        #data is dictionary = { 'start_time', 'start_frame', 'end_time', 'end_frame' }

        msg = defn.get_err_msg(result)
        print("GetVisualizeInfo return .. ", result, data)

        result = {
            'status' : status,
            'result' : result,
            'data' : data,
            'message' : msg
        }

        return result

@api.route('/kairos/mct/visualdata/<path:parameters>')
#<int:job_id>/<string:type>/<int:start_frame>/<int:end_frame>')
@api.doc()
class GetVsiaulizeData(Resource) :
    def get(self, parameters):
        print('GetVisualizeData : ', parameters)
        param_list = parameters.split('/')
        print(param_list)
        #comon : job_id, visualize_type
        #type1 : 'heatmap' : data is dictionary = { 'start_frame', 'end_frame' }
        #type2 : 'player_3d' on frame : {'target_frame' : }
        #type3 : 'player_2d' on frame at multi channel {'target_frame' : }
        task = {}
        job_id = param_list[0]

        if param_list[1] == '1' :
            task['type'] = 'heatmap'
        elif param_list[1] == '2' :
            task['type'] = 'player_3d'
        elif param_list[1] == '3' :
            task['type'] == 'player_2d'


        if (task['type'] == 'heatmap') :
            task['start_frame'] = param_list[2]
            task['end_frame'] = param_list[3]
            result, status, data = Commander().add_task(rc.GET_VISUAL_DATA, job_id, task) 
        
        elif (task['type'] == 'player_3d' or task['type'] == 'player_2d') :
            task['target_frame'] = param_list[2]
            result, status, data = Commander().add_task(rc.GET_VISUAL_DATA, job_id, task) 

        else :
            result = -117
            status = 0

        msg = defn.get_err_msg(result)

        result = {
            'status' : status,
            'result' : result,
            'data' : data,
            'message' : msg
        }

        return result

@api.route('/kairos/mct/get_version')
@api.doc()
class GetVersion(Resource) :
    def get(self) :
        print("call get version ")
        ver = defn().get_version() 
        print(ver)
        return {'result' : 'OK',
        'version' : ver}



if __name__ == '__main__':
    np = NewPool()
    DBLayer.initialize(np.getConn())

    Commander().start_commander()
    jr = Process(target=TaskManager.Watcher)
    jr.start()

    app.run(debug=False, host='0.0.0.0', port=9001)
