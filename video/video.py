import os
import cv2
import threading
import numpy as np


class Point:
    x = 0.0
    y = 0.0


class Video():

    def __init__(self, json, calib, world):
        print("video class is created")
        self.calib = calib
        self.len = len(json)

        self.address = []
        self.camIdx = []
        self.pts = []
        # put 3d points in pts
        for i in range(self.len):
            self.address.append(json[i]['address'])
            self.camIdx.append(json[i]['camIdx'])
            self.pts.append(
                [
                    (int(calib['points'][i]['pts_3d']['X1']),
                     int(calib['points'][i]['pts_3d']['Y1'])),
                    (int(calib['points'][i]['pts_3d']['X2']),
                     int(calib['points'][i]['pts_3d']['Y2'])),
                    (int(calib['points'][i]['pts_3d']['X3']),
                     int(calib['points'][i]['pts_3d']['Y3'])),
                    (int(calib['points'][i]['pts_3d']['X4']),
                     int(calib['points'][i]['pts_3d']['Y4']))
                ]
            )

        img_path = './/Soccer_Half.png'
        self.world_img = cv2.imread(img_path)

        # put world_points in dst_pts for find homo matrix
        self.dst_pts = []
        world_points = list()
        for i in range(4):
            p = Point()
            p.x = world[i][0]
            p.y = world[i][1]
            world_points.append(p)
        self.dst_pts = np.array([[e.x, e.y] for e in world_points])

    def find_Homo(self, index):
        calib = self.calib
        points = list()
        for i in range(4):
            p = Point()
            p.x = self.pts[index][i][0]
            p.y = self.pts[index][i][1]
            points.append(p)
        src_pts = np.array([[e.x, e.y] for e in points])

        H, status = cv2.findHomography(
            self.dst_pts, src_pts, cv2.RANSAC)       # world to channel
        # H, status = cv2.findHomography(src_pts, self.dst_pts, cv2.RANSAC)     # channel to world

        return H

    def calc_warp_pts(self, H, pts):
        x = (H[0][0]*pts[0] + H[0][1]*pts[1] + H[0][2]) / \
            (H[2][0]*pts[0] + H[2][1]*pts[1]+1)
        y = (H[1][0] * pts[0] + H[1][1] * pts[1] + H[1][2]) / \
            (H[2][0]*pts[0] + H[2][1]*pts[1] + 1)

        return (int(x), int(y))

    def draw_pts(self, index, frame):
        pts = self.pts

        for i in range(4):
            cv2.circle(frame, pts[index][i], 10, (0, 255, 0), 3)

        return frame

    def play(self, index):
        pt1 = (200, 530)
        pt2 = (240, 590)
        cv2.circle(self.world_img, pt1, 10, (120, 150, 0), -1)
        cv2.circle(self.world_img, pt2, 10, (20, 50, 200), -1)
        cv2.imshow('world image', self.world_img)

        h = self.find_Homo(index)

        pt1_warped = self.calc_warp_pts(h, pt1)
        pt2_warped = self.calc_warp_pts(h, pt2)

        cap = None
        try:
            cap = cv2.VideoCapture(self.address[index])
            if not cap.isOpened():
                raise IOError("Could not open video file.")

        except cv2.error as e:
            print(f"OpenCV exception: {e}")

        except IOError as e:
            print(f"Error: {e}")

        except Exception as e:
            print(f"Error: {e}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        idx = self.camIdx[index]

        while True:
            ret, frame = cap.read()
            if not ret:
                print('do not read video')
                break

            # tracking
            cv2.circle(frame, pt1_warped, 20, (120, 150, 0), -1)
            cv2.circle(frame, pt2_warped, 20, (20, 50, 200), -1)
            frame = self.draw_pts(index, frame)

            frame = cv2.resize(frame, (1920, 1080), cv2.INTER_AREA)
            cv2.imshow(idx, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                # if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def run(self):

        threads = []
        for index in range(self.len):
            print(index)
            thread = threading.Thread(target=self.play, args=(index,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
