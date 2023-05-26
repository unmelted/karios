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


@api.route('/kairos/ready')
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

        result, status = Commander().add_task(rc.TRACKER_READY, args)
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

@api.route('/kairos/start/<job_id>')
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


@api.route('/kairos/stop/<job_id>')
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
  
@api.route('/kairos/destroy/<job_id>')
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
        
@api.route('/kairos/status/<job_id>')
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

@api.route('/kairos/destroy/<job_id>')
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


@api.route('/kairos/get_version')
@api.doc()
class GetVersion(Resource) :
    def get(self) :
        print("call get version ")
        ver = defn().get_version() 
        print(ver)
        return {'result' : 'OK',
        'version' : ver}


@api.route('/kairos/get_visualinfo/<column>/<row>')
@api.doc()
class GetVisualInfo(Resource) :
    def get(self, columnn=column, row=row) :
        print("call GetVisualInfo ")
        result, status = Commander().add_task(rc.GET_VISUAL_INFO, column, row)

        msg = defn.get_err_msg(resulg)

        result = {
            'result' : result,
            'message' : msg
        }



if __name__ == '__main__':
    np = NewPool()
    DBLayer.initialize(np.getConn())

    Commander().start_commander()
    jr = Process(target=TaskManager.Watcher)
    jr.start()

    app.run(debug=False, host='0.0.0.0', port=9001)
