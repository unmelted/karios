import os
import time
import json
import cv2
import os.path
import warnings
from argparse import ArgumentParser
import mmcv
from mmpose.apis import (inference_bottom_up_pose_model, init_pose_model,
                         vis_pose_result)
from mmpose.datasets import DatasetInfo

from logger import Logger as l
from define import Definition as defn

class Pose(object) :
    init_done = False
    pose_model = None
    dataset = None
    dataset_info = None

    def __init__ (self) :
        if Pose.init_done == False:
            Pose.initialize()
            Pose.init_done = True

    @staticmethod
    def initialize() :
        l.get().w.debug("Pose initialize called ")

        Pose.pose_model = init_pose_model(
        defn.pose_config, defn.pose_checkpoint, device='cuda:0')
    
        Pose.dataset = Pose.pose_model.cfg.data['test']['type']
        Pose.dataset_info = Pose.pose_model.cfg.data['test'].get('dataset_info', None)
        if Pose.dataset_info is None:
            warnings.warn(
                'Please set `dataset_info` in the config.'
                'Check https://github.com/open-mmlab/mmpose/pull/663 for details.',
                DeprecationWarning)
            assert (Pose.dataset == 'BottomUpCocoDataset')
        else:
            Pose.dataset_info = DatasetInfo(Pose.dataset_info)

    @staticmethod
    def inference(image_name) :
        if Pose.init_done == False :
            initialize()

        pose_result, returned_outputs = inference_bottom_up_pose_model(
            Pose.pose_model,
            image_name,
            dataset=Pose.dataset,
            dataset_info=Pose.dataset_info,
            pose_nms_thr=defn.pose_nms_thr,
            return_heatmap=False,
            outputs=None)

        l.get().w.debug("Pose inference result pose : {}".format(pose_result))
        l.get().w.debug("Pose inference result  output : {}".format(returned_outputs))

        os.makedirs(args.out_img_root, exist_ok=True)
        out_file = os.path.join(
            defn.pose_dump,
            f'vis_{osp.splitext(os.path.basename(image_name))[0]}.jpg')

        # show the results
        vis_pose_result(
            Pose.pose_model,
            image_name,
            pose_results,
            radius=defn.pose_visualize_radius,
            thickness=defn.pose_visualuze_thick,
            dataset=Pose.dataset,
            dataset_info=Pose.dataset_info,
            kpt_score_thr=defn.pose_keypoint_thr,
            show=False, 
            out_file=out_file)

        return pose_result