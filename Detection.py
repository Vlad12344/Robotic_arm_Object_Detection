import numpy as np

def feature_vector(cordinates, angle, color):
    return [[cordinates['x'], cordinates['y'], cordinates['z'],
            np.deg2rad(angle), color]]
