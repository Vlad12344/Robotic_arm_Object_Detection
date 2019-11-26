import os
import cv2
import math
import numpy as np
import config
import os

from threading import Thread

class VideoStream:
    def __init__(self, src):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
        self.undistored = config.undistored
        self.calibration_mtx_dir = config.calibration_mtx_dir
        self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        self.stream.set(cv2.CAP_PROP_EXPOSURE, -4.5)

        if os.path.exists(self.calibration_mtx_dir) and self.undistored == True:
            self.cam_mtx = np.load(os.path.join(self.calibration_mtx_dir, 'cam_mtx.npy'))
            self.dist = np.load(os.path.join(self.calibration_mtx_dir, 'dist.npy'))
            self.newcam_mtx = np.load(os.path.join(self.calibration_mtx_dir, 'newcam_mtx.npy'))
        else:
            self.undistored = False

    def set_camera_resolution(self, resolution={'x': 640, 'y': 480}):
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, resolution['x'])
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution['y'])

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                self.stream.release()
                return
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
    # return the frame most recently read
        if not self.stream.isOpened():
            raise Exception("Could not open video device")
        if self.undistored:
            return self.undistort(self.frame)

        return self.frame

    def undistort(self, frame):
        dst = cv2.undistort(frame, self.cam_mtx, self.dist, None, self.newcam_mtx)

    def get_frame(self):
        if not self.stream.isOpened():
            raise Exception("Could not open video device")
        if self.undistored:
            return self.undistort(self.frame)

        return self.frame

    def stop(self):
        self.stopped = True
