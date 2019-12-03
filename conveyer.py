# from Camera import VideoStream
# from NNModel import Model
# from Utils import get_coordinates
# from processing.contour_processing import find_contours, angle_center, max_contour, watershed
# from Detection import feature_vector
# import cv2
#
# import numpy as np
# from math import sqrt
# import time
#
#
# def get_frame_list_in_time(frame_time):
#     stream = VideoStream(2)
#     stream.start()
#
#     frame_list = []
#
#     frame = stream.read()
#     cv2.imshow('hjk',frame)
#     start_time = time.time()
#     frame_list.append(frame)
#
#     while time.time() - start_time < frame_time:
#         continue
#
#     frame = stream.read()
#     cv2.imshow('hjk1', frame)
#     frame_list.append(frame)
#
#     stream.stop()
#
#     return frame_list
#
#
# def nothing(x):
#     pass
#
#
# def detect(frame_list):
#     nn_model = Model()
#
#     coordinates_list = []
#
#     for frame in frame_list:
#         predict = nn_model.predict(frame)[:, :, 0]
#
#         contours = find_contours(predict)
#
#         maximum_contour = max_contour(contours)
#         angle, centr = angle_center(maximum_contour)
#
#         coordinates = get_coordinates(xyz=[0, 0, 0.4], centr=centr)
#         coordinates_list.append(coordinates)
#
#     return coordinates_list
#
#
# def distance(coordinates):
#
#     euclidean_distance = sqrt(
#         (coordinates[0]['x'] - coordinates[1]['x']) ** 2 + (coordinates[0]['y'] - coordinates[1]['y']) ** 2)
#
#     return euclidean_distance
#
#
# def get_speed(led=0, time=0.25):
#     if led == True:
#         frame_list = get_frame_list_in_time(time)
#         coordinates = detect(frame_list)
#         speed = distance(coordinates) / time
#
#         return speed
#
#
# # cv2.namedWindow('image')
# #
# img = np.zeros((300, 300, 3), np.uint8)*255
#
#
# # switch = '0 : OFF \n1 : ON'
# # cv2.createTrackbar(switch, 'image', 0, 1, nothing)
# while True:
#     cv2.imshow('image', img)
#     k = cv2.waitKey(1) & 0xFF
#     if k == 27:
#         break
#     elif k==32:
#         speed = get_speed(1)
#         print(speed*3.6)
#         continue
#     # #
#     # # s = cv2.getTrackbarPos(switch, 'image')
#     # if s == 0:
#     #     continue
#     # else:
#     #     speed = get_speed(s)
#     #     print(speed)
#
#
#
# # cv2.destroyAllWindows()
