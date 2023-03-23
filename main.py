import os
import json
import ast
from multiprocessing import Process, Queue
from flask import Flask
from flask import request, jsonify
from flask_restx import fields, Resource, Api, reqparse, marshal

# from video import video as v
# from video.calibration import Calib
# from merger.merge import Merger


app = Flask(__name__)
api = Api(app, version='0.1', title='KAIROS')
app.config.SWAGGER_UI_DOC_EXPANSION = 'full'

conn_video = api.model('conn_vide', {
    'cams': fields.List(fields.Raw({"type": "RTSP",
 	 "address": "rtsp://admin:admin@10.82.5.129/3082_210_270.mp4",
 	 "camIdx": "003082"}, io="r"))
})


@api.route('/kairos/conn_video')
@api.doc()
class ConnVideo(Resource):
    @api.expect(conn_video)
    def post(self, model=conn_video):

        parser = reqparse.RequestParser()
        parser.add_argument('cams', default=list, action='append')
        args = parser.parse_args()

        cams = args['cams']
        cams_json = []
        for cam in cams:
            cam_json = json.loads(cam.replace("'", '"'))
            cams_json.append(cam_json)

        # Parse only the point value of the desired channel in the .pts file
        '''
        cal = Calib(cams_json)
        cal_data = cal.parse_pts()

        # Parse world points
        mer = Merger(cal_data)
        world_pts = mer.get_world_pts()

        # tracker API
        model_param = " " + cams_json[0]['address']
        print(model_param)
        os.system('python3 ' + config.tracker_api_dir + 'tracker_api_rtsp.py ' + model_param + ' &')

        # Play videos
        # vid = v.Video(cams_json, cal_data, world_pts)
        # vid.run()
        '''

        result = {
            'status': 0,
            'job_id': 0,
            'message': 'SUCCESS',
        }

        return result

@api.route('/kairos/get_version')
@api.doc()
class GetVersion(Resource) :
    def get(self) :
        print("call get version ")


if __name__ == '__main__':

    app.run(debug=False, host='0.0.0.0', port=3061)
