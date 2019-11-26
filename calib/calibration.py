import os
import sys
import cv2
import glob
import numpy as np

from os.path import dirname, join

project_root = dirname(dirname(__file__))
sys.path.insert(0, join(project_root, 'matrix'))
sys.path.insert(1, project_root)

from config import *
from Utils import save_matrix
from Mat import rot_x, rot_y, rot_z
from Mat import matrix_mult, transl, rot_2_euler
from math import cos, sin, radians, degrees, tan, sqrt, pi, atan2
from Mat import RRPosition_2_xyzrpw, xyzrpw_2_pose, pose_2_RRPosition, Pose_2_TxyzRxyz

COLIBRATION_POSITION = [[-0.2, -0.3, 0.3], [-3.14, 0, 0]]
NUMBER_OF_IMAGES = 30
CAMERA_INCLINATION = 20

def rm_files(folder):
    try:
        os.chdir(join(project_root, folder))
    except: AssertionError('Cant open folder. Check directory')

    if os.listdir(join(project_root, folder)) != []:
        files = glob.glob(join(project_root, folder, '/.*png'))
        for f in files:
            os.remove(f)
    pass

# def delta_phi():
#     if 4 <= NUMBER_OF_IMAGES <= 25:
#         return 2*pi / NUMBER_OF_IMAGES
#     raise AssertionError('Number of images must be in range from 4 to 25')

def hemisphere_point(radius, inclination):
    """
    Generate hemisphere and get point coordinate in random order

    :radius: is equal height of the camera
    :inclination: angle bitween vertical line and cone edge
    """
    if radius <= 0:
        raise AssertionError('Radius mast be grater than 0')

    alpha = np.random.rand() * pi*2
    r_small = radius*sin(radians(inclination))
    r = np.random.rand() * r_small

    # Find points on the sphere
    x = r * cos(alpha)
    y = r * sin(alpha)
    z = sqrt(radius**2 - x**2 - y**2)

    return x, y, z

def circle_point(radius, phi):
    """
    Generat point on circle provided by radius, and phi angle

    :param radius: circle radius
    :param phi: angle beetwin 0 and 2pi
    """
    if radius <= 0:
        raise AssertionError('Radius mast be grater than 0')
    x = radius * cos(radians(phi))
    y = radius * sin(radians(phi))
    z = 0

    return x, y, z

def get_calibration_point(position, inclination, phi=None):
    """
    Getting hemisphere point with respect to flange position

    :position: flange position
    :inclination: angle bitween vertical line and cone edge
    """
    if inclination <= 0 or inclination >= 50:
        raise AssertionError('inclination mast be grater than 0 and lower than 70')

    position = RRPosition_2_xyzrpw(position)
    radius = position[2]
    z_angle = position[5]
    position[2] = 0
    position[5] = 0

    x, y, z = hemisphere_point(radius,inclination)

    rz = rot_z(z_angle)
    ry = rot_y(-x/radius)
    rx = rot_x(-y/radius)

    t = transl([x,y,z])

    flange = xyzrpw_2_pose(position)
    point = pose_2_RRPosition(matrix_mult(t,flange,rx,ry,rz))

    return point

def camera_vectors(objpoints, imgpoints, img_path):
    """
    :param objpoints:
    :param imgpoints:
    :param gray:
    :return:
    """""
    gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    ret, cam_mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    return ret, cam_mtx, dist, rvecs, tvecs

def get_rotation_vector(objp, corners2, cam_mtx, dist):
    """
    Find euler angle of the chessboard.
    Its allows to know how the work plane is stand relative robot base.

    :param objp: chessboard corners points (in pixels)
    :param corners2:
    :param cam_mtx: 3x3 camera matrix.
                    [[fx 0 cx]
                     [0 fy cy]
                     [0  0  1]]
                     cx - centre along x axis pixels
                     cy - centre along y axis pixels
    :param dist: distortion coefficients
    :return: roll, pitch, yaw angles

    """
    # Find the rotation vector.
    _, rvecs, _, _ = cv2.solvePnPRansac(objp, corners2, cam_mtx, dist)
    rmat = cv2.Rodrigues(rvecs)[0]

    return rot_2_euler(rmat)

def objpnt_imgpnt_corner(img, cols=6, rows=9):
    """
    :param img: RGB chessboard image
    :param cols: Chessboard columns
    :param rows: Chessboard rows

    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objpoints = np.zeros((rows * cols, 3), np.float32)
    objpoints[:, :2] = np.mgrid[0:rows, 0:cols].T.reshape(-1, 2)
    # Arrays to store object points and image points from all the images.
    corners2 = np.zeros((cols*rows, 2))
    ret, imgpoints = cv2.findChessboardCorners(gray, (rows, cols), None)
    # If found, add object points, image points (after refining them)
    if ret:
        corners2 = cv2.cornerSubPix(gray, imgpoints, (11, 11), (-1, -1), criteria)

    return ret, objpoints, imgpoints, corners2

def save_camera_matrix(newcam_mtx, cam_mtx, dist):
    """
    Save matrix in npy format.
    Folder - project_root/data/cameradata

    :param newcam_mtx: np array, 3x3 dimansion
    :param cam_mtx: np array, 3x3 dimansion
    :param dist: distortion coefficient

    """
    save_matrix(join(project_root, 'data/cameradata/newcam_mtx.npy'), newcam_mtx)
    save_matrix(join(project_root, 'data/cameradata/cam_mtx.npy'), cam_mtx)
    save_matrix(join(project_root, 'data/cameradata/dist.npy'), dist)

def camera_matrix(resolution):
    """
    :param resolution: image resolution
    return newcam_mtx, cam_mtx, dist

    """
    images = glob.glob(join(project_root, 'images/calibration_imgs/*.png'))

    w = resolution[1]
    h = resolution[0]

    objpoints = []
    imgpoints = []

    for fname in images:
        img = cv2.imread(fname)
        ret, objpoint, imgpoint, corners2 = objpnt_imgpnt_corner(img)
        if ret:
            objpoints.append(objpoint)
            imgpoints.append(imgpoint)

    _, cam_mtx, dist, _, _ = camera_vectors(objpoints, imgpoints, images[np.random.randint(0,len(images))])
    newcam_mtx, _ = cv2.getOptimalNewCameraMatrix(cam_mtx, dist, (w, h), 1, (w, h))

    return newcam_mtx, cam_mtx, dist

def calibrate_plane(img):
    """
    """
    if not os.listdir(join(project_root, 'data/cameradata')) :
        return print("Directory is empty. Pleas calibrate your camera")

    cam_mtx = np.load(join(project_root, 'data/cameradata/cam_mtx.npy'))
    dist = np.load(join(project_root, 'data/cameradata/dist.npy'))

    ret, objpoints, imgpoints, corners2 = objpnt_imgpnt_corner(img)

    if ret:
        pitch, roll, yaw = get_rotation_vector(objpoints, corners2, cam_mtx, dist)
        return -roll, -pitch, yaw
    raise AssertionError('Bad image')

def distance_betwin_newplane_and_camera(imgpoints, object_natural_size_m):
    """
    Calculate distance beetwin camera and work plane
    """
    object_size_pix = np.max(imgpoints[:,0:9,0]) - np.min(imgpoints[:,0:9,0])
    size_on_matrix_m = PIXEL_SIZE * object_size_pix * CAMERA_RESOLUTION[0] / IMG_RESOLUTION[0]
    distance = object_natural_size_m * FOCAL_LENGTH / size_on_matrix_m

    return distance

# def is_rotation_matrix(R):
#     """
#     :param R:
#     :return:
#     """
#     Rt = np.transpose(R)
#     shouldbeidentity = np.dot(Rt, R)
#     I = np.identity(3, dtype=R.dtype)
#     n = np.linalg.norm(I - shouldbeidentity)
#     return n < 1e-6

# def rotation_matrix_to_euler_angles(R):
#     """
#     :param R:
#     :return:
#     """
#     R = R[0:3,0:3]
#     print(R)
#     assert (is_rotation_matrix(R))

#     sy = sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

#     singular = sy < 1e-6

#     if not singular:
#         x = atan2(R[2, 1], R[2, 2])
#         y = atan2(-R[2, 0], sy)
#         z = atan2(R[1, 0], R[0, 0])
#     else:
#         x = atan2(-R[1, 2], R[1, 1])
#         y = atan2(-R[2, 0], sy)
#         z = 0

#     return x, y, z



# newmtx, cam_mtx, dist = camera_matrix([640,480])
# save_camera_matrix(newmtx, cam_mtx, dist)

# roll, pitch, yaw = calibrate_plane(img)
