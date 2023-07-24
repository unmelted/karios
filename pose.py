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

    def __init__ (self) :
        self.pose_model = init_pose_model(
        defn.pose_config, defn.pose_checkpoint, device='cuda:0')
    
        self.dataset = self.pose_model.cfg.data['test']['type']
        self.dataset_info = self.pose_model.cfg.data['test'].get('dataset_info', None)
        if self.dataset_info is None:
            warnings.warn(
                'Please set `dataset_info` in the config.'
                'Check https://github.com/open-mmlab/mmpose/pull/663 for details.',
                DeprecationWarning)
            assert (self.dataset == 'BottomUpCocoDataset')
        else:
            self.dataset_info = DatasetInfo(self.dataset_info)

    def inference(self, image_name) :
        pose_result, returned_outputs = inference_bottom_up_pose_model(
            self.pose_model,
            image_name,
            dataset=self.dataset,
            dataset_info=self.dataset_info,
            pose_nms_thr=defn.pose_nms_thr,
            return_heatmap=False,
            outputs=None)

        l.get().w.error("Pose inference result pose : {}".format(pose_result))
        l.get().w.error("Pose inference result  output : {}".format(returned_outputs))

        os.makedirs(args.out_img_root, exist_ok=True)
        out_file = os.path.join(
            defn.pose_dump,
            f'vis_{osp.splitext(os.path.basename(image_name))[0]}.jpg')

        # show the results
        vis_pose_result(
            self.pose_model,
            image_name,
            pose_results,
            radius=defn.pose_visualize_radius,
            thickness=defn.pose_visualuze_thick,
            dataset=self.dataset,
            dataset_info=self.dataset_info,
            kpt_score_thr=defn.pose_keypoint_thr,
            show=False, 
            out_file=out_file)

        return pose_result