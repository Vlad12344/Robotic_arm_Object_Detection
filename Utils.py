import math
import numpy as np

from config import *
from matrix.Mat import transl, dim3_2_dim4, invH, transpose
from os.path import dirname, join

project_root = dirname(dirname(__file__))

# --------------------------------------------------------------
def tool_shift_mtx(tool_shift_x, tool_shift_y, tool_shift_z):
    return transl(tool_shift_x, tool_shift_y, tool_shift_z)
#---------------------------------------------------------------

def get_pose(xyz=None, centr=None):
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
    K = np.load(join(project_root, 'July_project\data\cameradata\\newcam_mtx.npy'))
    K = dim3_2_dim4(K)

    R = np.array([[0, 1, 0],
                  [1, 0, 0],
                  [0, 0, 1]])

    R = dim3_2_dim4(R)
    K_inv = invH(K)
    Z = z_relative_tothe_camera(xyz[2])
    # T_flange = np.array([xyz[0], xyz[1], 0])
    # T_cam = np.array(CAMERA_SHIFTING)
    # T = T_flange + T_cam
    # coordinates = K_inv.dot(X).dot(R) * Z + T
    pose = K_inv.dot(X).dot(R) * Z
    # return {'x':coordinates[0], 'y':coordinates[1], 'z':coordinates[2]}
    return pose

def get_coordinates(pose, flange_position, shifting):
    coordinates = pose.dot(transpose(flange_position)).dot(transpose(shifting))
    return {'x':coordinates[0], 'y':coordinates[1], 'z':coordinates[2]}

def save_matrix(path, matrix):
    return np.save(path, matrix)

def z_relative_tothe_camera(z):
    """
    Calculate distance between camera and object

    :param z: distance between end gripper point and base
    """
    new_z = z + TOOL_HEIGHT - CAMERA_SHIFTING[2] - OBJECT_HEIGHT
    return new_z

def distance_between_planes(z_old, z_new):
    """
    Calculate offset between base plane and work place. Need for changing robot base

    :param z_old: distance between end gripper point and zero base
    :param z_new: distance between camera matrix and chessboard calibration desk
    """
    # distance between camera matrix and zero base
    z_old = z_old + config.TOOL_HEIGHT + config.CAMERA_SHIFTING[2] - config.CHESSBOARD_THICKNESS

    return z_old - z_new

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
