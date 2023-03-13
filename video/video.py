import os
import cv2
import threading


class Video():

    def __init__(self, json):
        print("video class is created")
        print(json)

        self.len = len(json)
        print(self.len)
        self.address = []
        self.camIdx = []
        for i in range(self.len):
            print("ch ", i)
            self.address.append(json[i]['address'])
            self.camIdx.append(json[i]['camIdx'])
        # self.address.append(json[0]['address'])
        # self.camIdx.append(json[0]['camIdx'])
        print(json[0]['address'])

        # self.fps = self.cap.get(cv2.CAP_PROP_FPS)

    # def __init__(self, args):
    #     self.type = args['type']
    #     self.path = args['address']
    #     self.camIdx = args['camIdx']
    #     print("video class is created")
    #     # print(args)
    #     print("type : ", self.type)
    #     print("path : ", self.path)
    #     print("cam index : ", self.camIdx)

    def play(self, index):
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
