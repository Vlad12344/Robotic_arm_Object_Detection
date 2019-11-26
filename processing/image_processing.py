from __future__ import absolute_import

import cv2
import imutils
import numpy as np
from processing import contour_processing

from sklearn.cluster import MiniBatchKMeans

# --------------------------------------------------------------

def normalize(image):
    normalize_img = cv2.normalize(src=image, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX,
                                dtype=cv2.CV_8UC3)
    return normalize_img

# --------------------------------------------------------------

def white_balance(image, perc):
    """
    White balance for every channel independently

    :param channel: rgb channels of the image
    :param perc: percentile,where lower then 5-th percentile you find 5% of observations
    :return: new image white balanced
    """
    new_channel = []
    for channel in cv2.split(image):
        mi, ma = (np.percentile(channel, perc), np.percentile(channel, 100.0 - perc))
        channel = np.uint8(np.clip((channel - mi) * 255.0 / (ma - mi), 0, 255))
        new_channel.append(channel)

        imWB = np.dstack(new_channel)

    return imWB
# --------------------------------------------------------------

def image_saving(image, name='name.png'):
    # return cv2.imwrite(config.data_path + 'images/' + name, image)
    return cv2.imwrite('images/' + name, image)

# --------------------------------------------------------------

def eraze_backgraund(image, mask=None):
    return cv2.bitwise_and(image, image, mask=mask)

# --------------------------------------------------------------

def blur(img, ksize=(5,5)):
    return cv2.blur(img, ksize)

#--------------------------------------------------------------

def draw_bouding_box(image, contour, centr):
    box = contour_processing.get_bouding_box(contour)
    cv2.circle(image, (int(centr[0]), int(centr[1])), 3, (0, 0, 255), -1)
    image = cv2.drawContours(image, [box], 0, (0, 255, 0), 3)
    return image

#--------------------------------------------------------------

def draw_centr(centr):
    image = cv2.circle(image, (int(center[0]), int(center[1])), 3, (0, 0, 255), -1)
    return image