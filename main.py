import os
import json
import ast
from multiprocessing import Process, Queue
from flask import Flask
from flask import request, jsonify
from flask_restx import fields, Resource, Api, reqparse, marshal
# import definition as df
# from exodus import *
# from job_manager import JobManager
# from db_layer import NewPool, DBLayer
from video import video as v
from video.calibration import Calib
import threading

app = Flask(__name__)
api = Api(app, version='0.1', title='KAIROS')
app.config.SWAGGER_UI_DOC_EXPANSION = 'full'

##
conn_video = api.model('conn_vide', {
    'cams': fields.List(fields.Raw({"type": "String"}, io="r"))
})


@api.route('/kairos/conn_video')
@api.doc()
class ConnVideo(Resource):
    @api.expect(conn_video)
    def post(self, model=conn_video):

        parser = reqparse.RequestParser()
        # parser.add_argument('cams', default=list, action='split')
        parser.add_argument('cams', default=list, action='append')
        args = parser.parse_args()

        cam_len = len(args['cams'])

        cams = args['cams']
        cams_json = []
        for cam in cams:
            cam_json = json.loads(cam.replace("'", '"'))
            cams_json.append(cam_json)

        cal = Calib(cams_json)
        cal_data = cal.parse_pts()

        vid = v.Video(cams_json, cal_data)
        vid.run()

        result = {
            'status': 0,
            'job_id': 0,
            'message': 'SUCCESS',
        }

        return result


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3060)
