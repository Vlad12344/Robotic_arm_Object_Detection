import math
import numpy as np

from config import *
from matrix.Mat import transl
from os.path import dirname, join

project_root = dirname(dirname(__file__))

# --------------------------------------------------------------
def work_place_size(z):
    """
    :param z: distance between work place and camera. Measured in meters
    :return: work place height and width. Measured im meters
    """

    H = 2 * math.tan(math.radians(alpha) / 2) * z
    W = 2 * math.tan(math.radians(betta) / 2) * z

    return H, W
# --------------------------------------------------------------
def camera_matrix(z):
        """
            Getting the transformation matrix, that allows to
        transform pixels to mm

        :param z: distance between work place and camera. Measured in meters
        :return: transformation matrix

        Variables:

        W, H - workplace width and height in meters
        coef - transformation coefficient, that transformate pixels to meters
        """

        H, W = work_place_size(z)

        coef_x = W / resolution[1]
        coef_y = H / resolution[0]

        camera_matrix = np.array([[coef_x, 0, 0, -W / 2],
                                  [0, coef_y, 0, -H / 2],
                                  [0, 0, 1, 0],
                                  [0, 0, 0, 1]])

        return camera_matrix
# --------------------------------------------------------------
def camera_shift_mtx(camera_bias):
    return transl(camera_bias)
#---------------------------------------------------------------

def get_coordinates(xyz=None, centr=None):
    """
    Getting the center of the object relative robotic arm

    :param xyz: coordinates of the gripper, in the shot time
    :param center: object center in the image, gotten in pixels
    :return: center of the object relative robotic arm. type: np.array([x, y , z])

    Pinhole camera model

    K is a camera intrinsic matrix like [[f, 0, cx],
                                         [0, f, cy],
                                         [0, 0, 1]]
    f - camera focal length interpreted in pixels
    cx - distance (x) to the principal axis
    cy - distance (y) to the principal axis

    inv_K -> [[1/f, 0, -cx/f],
              [0, 1/f, -cy/f],
              [0, 0, 1]]

    R is a rotation matrix -> [[0, 1, 0], swap x and y axis
                               [1, 0, 0],
                               [0, 0, 1]]
    Camera axis -------x
                |
                |
                y

    Robot base -------y
               |
               |
               x

    Pixel_coord - matrix with centre coordinates (pixels)

    To find real coordinate -> inv_K * R * Pixel_coord + Flange_T + Camera_relative_flange_T

    Useful links:
    https://stackoverflow.com/questions/41503561/whats-the-difference-between-reprojectimageto3dopencv-and-disparity-to-3d-coo
    http://www.cs.cmu.edu/~16385/s17/Slides/11.1_Camera_matrix.pdf
    http://ais.informatik.uni-freiburg.de/teaching/ws09/robotics2/pdfs/rob2-08-camera-calibration.pdf

    """

    X = np.array([centr[0], centr[1], 1])
    K = np.load(join(project_root, 'Robotic_arm_Object_Detection/data/cameradata/newcam_mtx.npy'))

    R = np.array([[0, 1, 0],
                  [1, 0, 0],
                  [0, 0, 1]])
    Z = get_correct_z(xyz[2]) - CAMERA_SHIFTING[2] + TOOL_HEIGHT
    print(Z)
    K_inv = np.linalg.inv(K)
    T_flange = np.array([xyz[0], xyz[1], 0])
    T_cam = np.array(CAMERA_SHIFTING)
    T = T_flange + T_cam
    coordinates = K_inv.dot(X).dot(R) * Z + T

    return {'x':coordinates[0], 'y':coordinates[1], 'z':coordinates[2]}

def save_matrix(path, matrix):
    return np.save(path, matrix)

def get_correct_z(z):
    new_z = z + CAMERA_SHIFTING[2] - OBJECT_HEIGHT
    return new_z

def tic():
    """Start a stopwatch timer"""
    import time
    global TICTOC_START_TIME
    TICTOC_START_TIME = time.time()

def toc():
    """Read the stopwatch timer"""
    import time
    if 'TICTOC_START_TIME' in globals():
        elapsed = time.time() - TICTOC_START_TIME
        #print("Elapsed time is " + str(elapsed) + " seconds.")
        return elapsed
    else:
        print("Toc: start time not set")
        return -1
