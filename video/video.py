import os
import cv2
# import threading


class Video():

    def __init__(self, args):
        self.type = args['type']
        self.path = args['address']
        self.camIdx = args['camIdx']
        print("video class is created")
        # print(args)
        print("type : ", self.type)
        print("path : ", self.path)
        print("cam index : ", self.camIdx)

        try:
            self.cap = cv2.VideoCapture(self.path)
            if not self.cap.isOpened():
                raise IOError("Could not open video file.")

        except cv2.error as e:
            print(f"OpenCV exception: {e}")

        except IOError as e:
            print(f"Error: {e}")

        except Exception as e:
            print(f"Error: {e}")
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

    def play(self):

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print('do not read video')
                break

            # tracking

            frame = cv2.resize(frame, (1920, 1080), cv2.INTER_AREA)
            cv2.imshow(self.path, frame)

            if cv2.waitKey(int(1000/self.fps)) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
