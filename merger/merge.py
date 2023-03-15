import os
import cv2


class Merger():

    def __init__(self, data):
        print("Merger class is created")
        img_path = os.getcwd() + '\\Soccer_Half.png'

        world_img = cv2.imread(img_path)
        self.img = world_img

        print(data)
        world_pts = None
        for d in data['worlds']:
            if d['group'] == "Group2":
                world_pts = d['world_coords']

        pts = []
        pts.append(((int(world_pts['X1'])), int(world_pts['Y1'])))
        pts.append(((int(world_pts['X2'])), int(world_pts['Y2'])))
        pts.append(((int(world_pts['X3'])), int(world_pts['Y3'])))
        pts.append(((int(world_pts['X4'])), int(world_pts['Y4'])))

        print(pts)
        self.pts = pts

        # for i in range(4):
        #     cv2.circle(world_img, pts[i], 6, (0, 255, 100), 3)

        # cv2.imshow('world', world_img)
        # cv2.waitKey()

        # cv2.destroyAllWindows()

    def get_world_pts(self):
        return self.pts

        # cv2.imshow('world', self.img)
        # cv2.waitKey()
