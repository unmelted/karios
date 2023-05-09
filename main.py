import os

from multiprocessing import Process, Queue
from flask import Flask
from flask import request, jsonify
from flask_restx import fields, Resource, Api, reqparse, marshal

from define import Definition as defn
from define import RequestCategory as rc
from task import TaskManager
from db_layer import NewPool, DBLayer
from command import *


app = Flask(__name__)
api = Api(app, version='0.1', title='KAIROS')
app.config.SWAGGER_UI_DOC_EXPANSION = 'full'

ready_info = api.model('ready_info', {
    'task_id' : fields.String,
    'tracker' : fields.List(fields.Raw({ "type" : "String"}, io = 'r'))
})
'''
{
    task_id : ‘2023_0908_1534’,
    tracker : [

            {
               camera_id : ‘001101’,
               tracker_ip : ‘10.82.1.11’,
               stream_url : ‘rtsp://…’

             },
     ]
} 

'''

@api.route('/kairos/ready')
@api.doc()
class ready(Resource):
    @api.expect(ready_info)
    def post(self, model=ready_info):

        parser = reqparse.RequestParser()
        parser.add_argument('task_id', type=str)
        parser.add_argument('tracker', default=list, action='append')
        args = parser.parse_args()

        job_id = Commander.add_task(rc.TRACKER_READY,  args)
        result = {
            'status': 0,
            'job_id': 0,
            'message': 'SUCCESS',
        }

        return result

job_id = api.model('job_id', {
    'job_id': fields.String,
})

@api.route('/kairos/run/<job_id>')
@api.doc()
class Run(Resource) :
    def put(self, job_id=job_id):
        print("call Run ", job_id)
        return {'result' : 'OK'}


@api.route('/kairos/stop/<job_id>')
@api.doc()
class Stop(Resource) :
    def put(self, job_id=job_id):
        print("call stop" , job_id)
        return {'result' : 'OK'}        

@api.route('/kairos/status/<job_id>')
@api.doc()
class GetStatus(Resource) :
    def get(self, job_id=job_id):
        print("call status ", job_id)
        return {'result' : 'OK'}

@api.route('/kairos/get_version')
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
    
    # que = Commander.get_cmdq()
    pr = Process(target=Commander.receiver)
    mr = Process(target=Commander.receiver_msg)    
    jr = Process(target=TaskManager.Watcher)

    pr.start()
    mr.start()
    jr.start()

    app.run(debug=False, host='0.0.0.0', port=9001)
