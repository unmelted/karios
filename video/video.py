import os
import cv2
import threading


class Video():

    def __init__(self, json, calib):
        print("video class is created")
        # print(json)
        print(calib)
        self.calib = calib

        self.len = len(json)

        self.address = []
        self.camIdx = []
        self.pts = []
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
        print(self.pts)

    def draw_pts(self, index, frame):
        pts = self.pts

        for i in range(4):
            # print(i)
            # print(pts[index][i])
            cv2.circle(frame, pts[index][i], 10, (0, 255, 0), 3)
        # cv2.circle(frame,)

        return frame

    def play(self, index):
        print("idx : ", self.camIdx[index])
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
            frame = self.draw_pts(index, frame)

            frame = cv2.resize(frame, (1920, 1080), cv2.INTER_AREA)
            cv2.imshow(idx, frame)

            if cv2.waitKey(10) & 0xFF == ord('q'):
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

        # self.play(0)
