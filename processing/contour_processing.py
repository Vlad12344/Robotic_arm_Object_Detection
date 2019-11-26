from __future__ import absolute_import

import cv2
import imutils
import numpy as np

from scipy import ndimage
from processing import image_processing
from skimage.feature import peak_local_max

def find_contours(mask):
    mask = image_processing.normalize(mask)
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    return contours
# --------------------------------------------------------------
def max_contour(contours):
    return max(contours, key=cv2.contourArea)
# --------------------------------------------------------------
def get_bouding_box(contour):
    bouding_box = cv2.minAreaRect(contour)
    bouding_box = cv2.boxPoints(bouding_box)

    return np.array(bouding_box, dtype='int')
# --------------------------------------------------------------
def watershed(gray):
    # convert image to dtype=cv2.CV_8UC1
    normalized_img = image_processing.normalize(gray)
    bgr = cv2.cvtColor(normalized_img, cv2.COLOR_GRAY2BGR)

    thresh = cv2.threshold(normalized_img, 0, 255,
                            cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # noise removal
    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 1)
    # sure background area
    sure_bg = cv2.dilate(opening,kernel,iterations=1)
    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
    ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)
    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)
    # Marker labelling
    ret, markers = cv2.connectedComponents(sure_fg)
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers+1
    # Now, mark the region of unknown with zero
    markers[unknown==255] = 0
    # # compute the exact Euclidean distance from every binary
    # # pixel to the nearest zero pixel, then find peaks in this
    # # distance map
    # D = ndimage.distance_transform_edt(thresh)
    # localMax = peak_local_max(D, indices=False, min_distance=20,
    #                             labels=thresh)

    # # perform a connected component analysis on the local peaks,
    # # using 8-connectivity, then apply th.predict(img)
    # markers = ndimage.label(localMax, structure=np.ones((3, 3)))[0]
    # markers = cv2.normalize(src=markers, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX,
    #                             dtype=cv2.CV_32SC1)
    # contours = cv2.watershed(normalized_img, markers)

    contours = cv2.watershed(bgr,markers)
    contours = np.argwhere(contours[1:-1,1:-1] == -1)
    return contours
# --------------------------------------------------------------
def angle_center(contour):
    # find the angle of rotation
    my_rotate_rect = cv2.minAreaRect(contour)

    angle = my_rotate_rect[2]
    centr = my_rotate_rect[0]

    # it make for decreasing the angle of rotation
    if -45 > angle > -90:
        angle = angle + 90
    elif angle == -90:
        angle = 0
    else:
        angle = angle

    return angle, centr
# --------------------------------------------------------------
def choose_contours(contours, low_level=4000, up_level=9000):
    return [i for i in contours if up_level > cv2.contourArea(i) > low_level]
# --------------------------------------------------------------
def sort_contours(cnts, reverse=True):
	return sorted(cnts, key=cv2.contourArea, reverse=reverse)
# --------------------------------------------------------------
