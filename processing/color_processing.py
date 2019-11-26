from __future__ import absolute_import

import cv2
import pickle
import numpy as np
from processing import image_processing
from config import data_path

# --------------------------------------------------------------

def mean_color_in_contour(image, contour):
    mask = np.zeros(image.shape[:2], dtype="uint8")
    mask = cv2.fillConvexPoly(mask, contour, 255)
    img = image_processing.eraze_backgraund(image, mask=mask)
    normalize_img = image_processing.normalize(img)
    mean_val = cv2.mean(normalize_img, mask=mask)
    mean_color = np.array([[mean_val[2], mean_val[1], mean_val[0]]], dtype='uint8')

    return mean_color

# --------------------------------------------------------------

def predict_color(mean):
    """
    Load k_means weights and predict object color

    :param mean: mean color of the object with parameters R,G,B
    :return: color in number format
    """
    loaded_model = pickle.load(open(data_path + 'k-means/k_means_colors.sav', 'rb'))
    result = loaded_model.predict(mean)

    return str(result[0])

# --------------------------------------------------------------

def bgr2lab(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

# --------------------------------------------------------------