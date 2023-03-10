import os
from multiprocessing import Process, Queue
from flask import Flask
from flask import request, jsonify
from flask_restx import fields, Resource, Api, reqparse, marshal
# import definition as df
# from exodus import *
# from job_manager import JobManager
# from db_layer import NewPool, DBLayer
from video import video
import threading

app = Flask(__name__)
api = Api(app, version='0.1', title='KAIROS')
app.config.SWAGGER_UI_DOC_EXPANSION = 'full'

##
conn_video = api.model('conn_vide', {
    'type': fields.String,
    'address': fields.String,
    'camIdx': fields.String
})


@api.route('/kairos/conn_video')
@api.doc()
class ConnVideo(Resource):
    @api.expect(conn_video)
    def post(self, model=conn_video):

        parser = reqparse.RequestParser()
        parser.add_argument('type', type=str)
        parser.add_argument('address', type=str)
        parser.add_argument('camIdx', type=str)
        args = parser.parse_args()
        print(args)

        vid = video.Video(args)
        # vid.play()

        # test multi thread
        video_list = []
        video_list.append(args['address'])
        video_list.append(args['address'])
        print(video_list)

        # players = [video.Video(vi) for vi in video_list]
        # threads = [threading.Thread(target=player.play) for player in players]

        # for thread in threads:
        #     thread.start()
        # for thread in threads:
        #     thread.join()

        result = {
            'status': 0,
            'job_id': 0,
            'message': 'SUCCESS',
        }

        return result


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3060)
