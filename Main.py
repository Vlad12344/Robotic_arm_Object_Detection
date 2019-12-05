from pulseapi import RobotPulse, position, PulseApiException, pose, MotionStatus, MT_LINEAR, tool_info, tool_shape, Point, create_simple_capsule_obstacle
from PyQt5.QtWidgets import QApplication, QMessageBox, QShortcut
from PyQt5.QtGui import QKeySequence
import sys
import math
import numpy as np
import Utils

from processing.contour_processing import max_contour, angle_center, find_contours, sort_contours
from processing.color_processing import mean_color_in_contour, predict_color
from processing.image_processing import image_saving, draw_bouding_box, eraze_backgraund, white_balance
from Detection import feature_vector
from Camera import VideoStream
from NNModel import Model
from UI import UI
from K_Means_model import K_Means
import cv2
import time

# Настройка робота
robot = RobotPulse('10.10.10.20:8081')

# Вызов UI
app = QApplication(sys.argv)
interface = UI(app)
interface.show()

# Инициализация и подгрузка нейронной сети, задание смещения камеры
nn_model = Model()
KMeans = K_Means()
stream = VideoStream(0)
robot.change_base(position([0,0,0], [0, 0, 0]))
roll, pitch = -0.016667, 0.012
robot.change_base(position([0,0,-0.132], [-roll, -pitch, 0]))
src = 0

def create_tool(radius, height, name):
    """
    The tool is created as cylinder with R = radius and H = height
    Important step in work process.
    With it help robot calculate trajectory considering his gripper/tool

    :param radius: cylinder radius
    :param height: cylinder height
    """
    if 0 <= radius <= 0.3 and 0 <= height <= 0.3:
        # create new tool properties
        new_tool_info = tool_info(position([0, 0, height], [0, 0, 0]), name=name)
        new_tool_shape = tool_shape(
            [create_simple_capsule_obstacle(radius, Point(0, 0, 0), Point(0, 0, height))])
        # change tool properties
        robot.change_tool_info(new_tool_info)
        robot.change_tool_shape(new_tool_shape)
    else:
        raise AssertionError('Incorrect tool parameters')

create_tool(0.075, 0.070, name='Soska')

def detect(img, robot_position):
    predict = nn_model.predict(img)[:,:,0]
    contours = find_contours(predict)
    maximum_contour = max_contour(contours)
    angle, centre = angle_center(maximum_contour)
    mean_color = mean_color_in_contour(img, maximum_contour)
    coordinates = Utils.get_pose(xyz=robot_position, centr=centre)
    predicted_color = KMeans.predict(mean_color)
    mask = eraze_backgraund(img, mask=predict)
    # image_with_bbox = draw_bounding_box(img, maximum_contour, centr)
    # image_saving(mask, name="{}.png".format(np.random.randint(0,1000)))
    features = [feature_vector(coordinates, angle, predicted_color)]
    return features

# def detect(img, robot_position):
#     predict = nn_model.predict(img)[:,:,0]
#     image_saving(predict, name='predict.png')
#     # background_off = erase_background(img, mask=predict)
#     contours = find_contours(predict)
#     contours = sort_contours(contours)[0:5]
#     features_ = []

#     for contour in contours:
#         angle, centre = angle_center(contour)
#         mean_color = mean_color_in_contour(img, contour)
#         coordinates = Utils.get_pose(xyz=robot_position, centr=centre)
#         predicted_color = KMeans.predict(mean_color)
#         # mask = eraze_backgraund(img, mask=predict)
#         # image_with_bbox = draw_bounding_box(img, maximum_contour, centr)
#         # image_saving(mask, name="{}.png".format(np.random.randint(0,1000)))
#         features_.append(feature_vector(coordinates, angle, predicted_color))

#     return features_

# Задание дополнительного смещения
SHIFT_LIST = [math.pi, 0, -math.pi/4]

# Извлечение координат x, y, z из robot.get_position()
def get_coordinates(data):
    data = str(data)
    data = data.split('\n')
    x_coordinate = data[0][(data[0].rfind(' ') + 1):data[0].rfind(',')]
    y_coordinate = data[1][(data[1].rfind(' ') + 1):data[1].rfind(',')]
    z_coordinate = data[2][(data[2].rfind(' ') + 1):data[2].rfind('}')]
    coordinates = [x_coordinate, y_coordinate, z_coordinate]
    for i in range(len(coordinates)):
        if coordinates[i][0] == "-":
            coordinates[i] = -float(coordinates[i][1:])
        else:
            coordinates[i] = float(coordinates[i])
    return coordinates

def takeMyCurrentPoint(state):
    reply = QMessageBox.question(
        interface, 'Внимание!',
        "Перезаписать эту крайнюю точку текущим положением?",
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.Yes:
        if state == 0:
            currentPoint = get_coordinates(robot.get_position())
            interface.entry_camera_x2.setText(str(round(currentPoint[0], 3)))
            interface.entry_camera_y2.setText(str(round(currentPoint[1], 3)))
            interface.entry_camera_z2.setText(str(round(currentPoint[2], 3)))
            interface.d[state] = [currentPoint[0],
                                currentPoint[1],
                                currentPoint[2]]
            np.save('data/log/starting_coordinates.npy', interface.d)
        if state == 1:
            currentPoint = get_coordinates(robot.get_position())
            interface.entry_camera_x1.setText(str(round(currentPoint[0], 3)))
            interface.entry_camera_y1.setText(str(round(currentPoint[1], 3)))
            interface.entry_camera_z1.setText(str(round(currentPoint[2], 3)))
            interface.d[state] = [currentPoint[0],
                                currentPoint[1],
                                currentPoint[2]]
            np.save('data/log/starting_coordinates.npy', interface.d)
        if state == 2:
            currentPoint = get_coordinates(robot.get_position())
            interface.entry_pallet_x2.setText(str(round(currentPoint[0], 3)))
            interface.entry_pallet_y2.setText(str(round(currentPoint[1], 3)))
            interface.entry_pallet_z2.setText(str(round(currentPoint[2], 3)))
            interface.d[state] = [currentPoint[0],
                                currentPoint[1],
                                currentPoint[2]]
            np.save('data/log/starting_coordinates.npy', interface.d)
        if state == 3:
            currentPoint = get_coordinates(robot.get_position())
            interface.entry_pallet_x1.setText(str(round(currentPoint[0], 3)))
            interface.entry_pallet_y1.setText(str(round(currentPoint[1], 3)))
            interface.entry_pallet_z1.setText(str(round(currentPoint[2], 3)))
            interface.d[state] = [currentPoint[0],
                                currentPoint[1],
                                currentPoint[2]]
            np.save('data/log/starting_coordinates.npy', interface.d)

def define_camera_place():
    interface.furthest_corner = [float(interface.entry_camera_x2.text()),
                            float(interface.entry_camera_y2.text()),
                            float(interface.entry_camera_z2.text())]
    interface.nearest_corner = [float(interface.entry_camera_x1.text()),
                            float(interface.entry_camera_y1.text()),
                            float(interface.entry_camera_z1.text())]
    camera_x_coordinate = (
        interface.furthest_corner[0] + interface.nearest_corner[0]) / 2 + 0.035
    camera_y_coordinate = (
        interface.furthest_corner[1] + interface.nearest_corner[1]) / 2 + 0.065
    camera_coordinates = position(
        [camera_x_coordinate, camera_y_coordinate, 0.45], [math.pi, 0, -math.pi/4])
    return camera_coordinates

def set_home_position():
    reply = QMessageBox.question(interface, 'Внимание',
                                 "Робот перейдёт в начальное положение со скоростью {}.".format(
        interface.comboSpeed.currentText()),
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
    if reply == QMessageBox.Ok:
        robot.set_pose(pose([0, -90, 0, -90, -90, 0]), int(interface.comboSpeed.currentText()))

def set_camera_position():
    reply = QMessageBox.question(interface, 'Внимание',
                                 "Робот перейдёт в положение камеры со скоростью {}.".format(
        interface.comboSpeed.currentText()),
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
    if reply == QMessageBox.Ok:
        robot.set_position(camera_position, int(interface.comboSpeed.currentText()))

def keyboardControl(key):
    try:
        current_position = robot.get_position()
        xyz_list = get_coordinates(current_position)
        if key == 'W':
            robot.set_position(position([xyz_list[0],
                                            xyz_list[1] - 0.05,
                                            xyz_list[2]],
                                            [SHIFT_LIST[0],
                                             SHIFT_LIST[1],
                                             SHIFT_LIST[2]]), 10)
            robot.await_motion(asking_interval=0.001)
        elif key == 'A':
            robot.set_position(position([xyz_list[0] + 0.05,
                                            xyz_list[1],
                                            xyz_list[2]],
                                            [SHIFT_LIST[0],
                                             SHIFT_LIST[1],
                                             SHIFT_LIST[2]]), 10)
            robot.await_motion(asking_interval=0.001)
        elif key == 'S':
            robot.set_position(position([xyz_list[0],
                                            xyz_list[1] + 0.05,
                                            xyz_list[2]],
                                            [SHIFT_LIST[0],
                                             SHIFT_LIST[1],
                                             SHIFT_LIST[2]]), 10)
            robot.await_motion(asking_interval=0.001)
        elif key == 'D':
            robot.set_position(position([xyz_list[0] - 0.05,
                                            xyz_list[1],
                                            xyz_list[2]],
                                            [SHIFT_LIST[0],
                                             SHIFT_LIST[1],
                                             SHIFT_LIST[2]]), 10)
            robot.await_motion(asking_interval=0.001)
        elif key == 'Space':
            robot.set_position(position([xyz_list[0],
                                            xyz_list[1],
                                            xyz_list[2] + 0.01],
                                            [SHIFT_LIST[0],
                                             SHIFT_LIST[1],
                                             SHIFT_LIST[2]]), 10)
            robot.await_motion(asking_interval=0.001)
        elif key == 'C':
            robot.set_position(position([xyz_list[0],
                                            xyz_list[1],
                                            xyz_list[2] - 0.01],
                                            [SHIFT_LIST[0],
                                             SHIFT_LIST[1],
                                             SHIFT_LIST[2]]), 10)
            robot.await_motion(asking_interval=0.001)
        elif key == 'Q':
            robot.open_gripper(1)
        elif key == 'E':
            robot.close_gripper(1)
        # print(get_coordinates(current_position))
    except PulseApiException as e:
        QMessageBox.warning(
            interface, 'Внимание!',
            "Робот не может двигаться в дальнейшем направлении!.",
            QMessageBox.Ok)
        if robot.status_motion() == MotionStatus.ERROR:
            robot.recover()
            print('Robot recovered from error')

def getting_started():
    global pallet_y, pallet_x, speed, detail_size, between_details, CURRENT_COLOR, CURRENT_BLOCK, pallet_furthest_point
    pallet_y = int(interface.comboHeightPallet.currentText())
    pallet_x = int(interface.comboWidthPallet.currentText())
    speed = int(interface.comboSpeed.currentText())
    detail_size = float(interface.entrySize.text())
    between_details = float(interface.entryBetween.text())
    CURRENT_COLOR = ''
    CURRENT_BLOCK = 0
    interface.autoColors()
    pallet_furthest_point = [float(interface.entry_pallet_x2.text()),
                                    float(interface.entry_pallet_y2.text()),
                                    float(interface.entry_pallet_z2.text())]
    if interface.enableColorPalletising.isChecked():
        reply = QMessageBox.question(interface, 'Внимание',
                                    'Робот запустится со следующими параметрами:\n'
                                    '- скорость движения робота {};\n'
                                    '- размер детали {};\n'
                                    '- расстояние между деталями {}.\n'
                                    'Режим работы - раскладка по цветам.\n'
                                    'Порядок цветов - {}\n'.format(
                                        int(interface.comboSpeed.currentText()),
                                        float(interface.entrySize.text()),
                                        float(interface.entryBetween.text()),
                                        list(interface.PALLET_LIST)),
                                    QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if reply == QMessageBox.Ok:
            stream.start()
            color_pallet()

    elif not interface.enableColorPalletising.isChecked():
        reply = QMessageBox.question(interface, 'Внимание',
                                        'Робот запустится со следующими параметрами:\n'
                                        '- высота паллета {}, ширина паллета {};\n'
                                        '- скорость движения робота {};\n'
                                        '- размер детали {};\n'
                                        '- расстояние между деталями {}.\n'
                                        'Режим работы - паллетирование.\n'
                                        'Раскладывать списком - {}'.format(
                                            int(interface.comboHeightPallet.currentText()),
                                            int(interface.comboWidthPallet.currentText()),
                                            int(interface.comboSpeed.currentText()),
                                            float(interface.entrySize.text()),
                                            float(interface.entryBetween.text()),
                                            interface.enableAllDetails.isChecked()
                                        ),
                                    QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if reply == QMessageBox.Ok:
            stream.start()
            pallet()

def pick_new_block():
    global speed, img, features
    speed = int(interface.comboSpeed.currentText())
    robot.set_position(camera_position, speed)
    robot.await_motion(asking_interval=0.001)
    img = stream.read()
    features = detect(img,get_coordinates(robot.get_position()))
    if interface.enableColorPalletising.isChecked() or not interface.enableAllDetails.isChecked():
        if type(features) != str:
            # robot.set_position(position([features[0][0], features[0][1], 0.35],
            #                             [SHIFT_LIST[0], SHIFT_LIST[1], SHIFT_LIST[2]]),
            #                             speed)
            target_positions=[position([features[0][0], features[0][1], 0.04], [SHIFT_LIST[0], SHIFT_LIST[1], SHIFT_LIST[2]]),
                              position([features[0][0], features[0][1], 0.15], [SHIFT_LIST[0], SHIFT_LIST[1], SHIFT_LIST[2]])]

            robot.await_motion(asking_interval=0.01)
            robot.set_position(position([features[0][0], features[0][1], 0.04],
                                        [SHIFT_LIST[0], SHIFT_LIST[1], SHIFT_LIST[2]]),
                                        speed,
                                        motion_type=MT_LINEAR)
            robot.await_motion(asking_interval=0.001)
            robot.open_gripper(1)
            robot.set_position(position([features[0][0], features[0][1], 0.15],
                                        [SHIFT_LIST[0], SHIFT_LIST[1], SHIFT_LIST[2]]),
                                        speed,
                                        motion_type=MT_LINEAR)
            robot.await_motion(asking_interval=0.001)
            # robot.run_positions(target_positions[0], velocity=speed, motion_type=MT_LINEAR)
            # robot.await_motion(0.001)
            # robot.run_positions(target_positions[1], velocity=speed, motion_type=MT_LINEAR)
            # robot.await_motion(0.001)
            # robot.open_gripper(1)
            return 'Continue'
        else:
            return None
    elif not interface.enableColorPalletising.isChecked() or interface.enableAllDetails.isChecked():
        if type(features) != str:
            target_positions = [position([features[CURRENT_BLOCK][0], features[CURRENT_BLOCK][1], 0.15], [SHIFT_LIST[0], SHIFT_LIST[1], SHIFT_LIST[2]]),
                                position([features[CURRENT_BLOCK][0], features[CURRENT_BLOCK][1], 0.04], [SHIFT_LIST[0], SHIFT_LIST[1], SHIFT_LIST[2]])]

            # robot.run_positions(target_positions[0:2], velosity=speed, motion_type=MT_LINEAR)
            # robot.open_gripper(1)
            # robot.run_positions(target_positions[0], velocity=speed, motion_type=MT_LINEAR)

            # robot.set_position(position([features[CURRENT_BLOCK][0],
            #                             features[CURRENT_BLOCK][1],
            #                             0.15],
            #                             [SHIFT_LIST[0], SHIFT_LIST[1], SHIFT_LIST[2]]),
            #                             speed)
            # robot.await_motion(asking_interval=0.001)
            robot.set_position(position([features[CURRENT_BLOCK][0],
                                        features[CURRENT_BLOCK][1],
                                        0.04],
                                        [SHIFT_LIST[0], SHIFT_LIST[1], SHIFT_LIST[2]]),
                                        speed,
                                        motion_type=MT_LINEAR)
            robot.await_motion(asking_interval=0.001)
            robot.open_gripper(1)
            robot.set_position(position([features[CURRENT_BLOCK][0],
                                        features[CURRENT_BLOCK][1],
                                        0.15],
                                        [SHIFT_LIST[0],
                                        SHIFT_LIST[1],
                                        SHIFT_LIST[2]]),
                                        speed,
                                        motion_type=MT_LINEAR)
            robot.await_motion(asking_interval=0.001)
            return 'Continue'
        else:
            return None

def pallet():
    global pallet_y, pallet_x, speed, detail_size, between_details, CURRENT_COLOR, CURRENT_BLOCK, pallet_furthest_point
    if interface.enableAllDetails.isChecked():
        speed = int(interface.comboSpeed.currentText())
        robot.set_position(camera_position, speed)
        robot.await_motion(asking_interval=0.001)
        img = stream.read()
        # features = detect(img, get_coordinates(robot.get_position()))
        # new = SHIFT_LIST[2] - float(features[0][3])

    for y in range(pallet_y):
        for x in range(pallet_x):
            state = pick_new_block()
            if state == 'Continue':
                next_x = pallet_furthest_point[0] - x * \
                    (detail_size + between_details)
                next_y = pallet_furthest_point[1] + y * \
                    (detail_size + between_details)
                new = SHIFT_LIST[2] - float(features[0][3])
                robot.set_position(position([next_x, next_y, 0.15],
                                            [SHIFT_LIST[0],
                                                SHIFT_LIST[1],
                                                new]),
                                    speed)
                robot.await_motion(asking_interval=0.001)
                robot.set_position(position([next_x, next_y, 0.04],
                                            [SHIFT_LIST[0],
                                                SHIFT_LIST[1],
                                                new]),
                                    speed,
                                    motion_type=MT_LINEAR)
                robot.await_motion(asking_interval=0.001)
                robot.close_gripper(1)
                # robot.set_position(position([next_x, next_y, 0.15],
                #                             [SHIFT_LIST[0],
                #                                 SHIFT_LIST[1],
                #                                 new]),
                #                     speed,
                #                     motion_type=MT_LINEAR)
                robot.await_motion(asking_interval=0.001)
                CURRENT_BLOCK += 1
            else:
                reply = QMessageBox.question(interface, 'Внимание',
                                                "Робот разложил {} кубиков, не обнаружил других "
                                                "и возвращается в начальное положение.".format(
                                                    CURRENT_BLOCK),
                                                QMessageBox.Ok, QMessageBox.Ok)
                if reply == QMessageBox.Ok:
                    stream.stop()
                    robot.set_pose(pose([0, -90, 0, -90, -90, 0]), 10)
                    return None
    set_camera_position()
    reply = QMessageBox.question(interface, 'Внимание',
                                    "Робот разложил все {} кубиков "
                                    "и возвращается в начальное положение.".format(
                                        CURRENT_BLOCK),
                                    QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
    if reply == QMessageBox.Ok:
        stream.stop()
        robot.set_pose(pose([0, -90, 0, -90, -90, 0]), 10)
    return None

def color_pallet():
    global pallet_y, pallet_x, speed, detail_size, between_details, CURRENT_COLOR, CURRENT_BLOCK, pallet_furthest_point
    state = pick_new_block()
    if state == 'Continue':
        CURRENT_COLOR = str(features[0][4])
        if interface.enableAutoColors.isChecked() and CURRENT_COLOR not in interface.PALLET_LIST:
            new = SHIFT_LIST[2] - float(features[0][3])
            # создание пары "новый цвет-пустой список"
            interface.PALLET_LIST.update({CURRENT_COLOR: []})
            interface.PALLET_LIST[CURRENT_COLOR].append(
                len(interface.PALLET_LIST[CURRENT_COLOR]))
            CURRENT_PALLET_X = len(interface.PALLET_LIST[CURRENT_COLOR]) - 1
            CURRENT_PALLET_Y = list(
                interface.PALLET_LIST.keys()).index(CURRENT_COLOR)
            next_x = pallet_furthest_point[0] - CURRENT_PALLET_X * (
                detail_size + between_details)
            next_y = pallet_furthest_point[1] + CURRENT_PALLET_Y * (
                detail_size + between_details)
            robot.set_position(position([next_x, next_y, 0.15],
                                [SHIFT_LIST[0], SHIFT_LIST[1], new]),
                                speed)
            robot.await_motion(asking_interval=0.001)
            robot.set_position(position([next_x, next_y, 0.04],
                                [SHIFT_LIST[0], SHIFT_LIST[1], new]),
                                speed,
                                motion_type=MT_LINEAR)
            robot.await_motion(asking_interval=0.001)
            robot.close_gripper(1)
            robot.set_position(position([next_x, next_y, 0.06],
                                [SHIFT_LIST[0], SHIFT_LIST[1], new]),
                                speed,
                                motion_type=MT_LINEAR)
            robot.await_motion(asking_interval=0.001)
            CURRENT_BLOCK += 1
            color_pallet()
        else:
            new = SHIFT_LIST[2] - float(features[0][3])
            interface.PALLET_LIST[CURRENT_COLOR].append(
                len(interface.PALLET_LIST[CURRENT_COLOR]))
            CURRENT_PALLET_X = len(interface.PALLET_LIST[CURRENT_COLOR]) - 1
            CURRENT_PALLET_Y = list(
                interface.PALLET_LIST.keys()).index(CURRENT_COLOR)
            next_x = pallet_furthest_point[0] - CURRENT_PALLET_X * (
                detail_size + between_details)
            next_y = pallet_furthest_point[1] + CURRENT_PALLET_Y * (
                detail_size + between_details)
            robot.set_position(position([next_x, next_y, 0.15],
                                [SHIFT_LIST[0], SHIFT_LIST[1], new]),
                                speed)
            robot.await_motion(asking_interval=0.001)
            robot.set_position(position([next_x, next_y, 0.04],
                                [SHIFT_LIST[0], SHIFT_LIST[1], new]),
                                speed,
                                motion_type=MT_LINEAR)
            robot.await_motion(asking_interval=0.001)
            robot.close_gripper(1)
            robot.set_position(position([next_x, next_y, 0.06],
                                [SHIFT_LIST[0], SHIFT_LIST[1], new]),
                                speed,
                                motion_type=MT_LINEAR)
            robot.await_motion(asking_interval=0.001)
            CURRENT_BLOCK += 1
            color_pallet()
    else:
        reply = QMessageBox.question(interface, 'Внимание',
                                        "Робот разложил {} кубиков и не обнаружил других."
                                        "Вернуться в начальное положение или попробовать обнаружить ещё?".format(
                                            CURRENT_BLOCK),
                                        QMessageBox.Ok | QMessageBox.Retry, QMessageBox.Retry)
        if reply == QMessageBox.Ok:
            stream.stop()
            robot.set_pose(pose([0, -90, 0, -90, -90, 0]), 10)
            return None
        elif reply == QMessageBox.Retry:
            color_pallet()
        return None



# Определение позиции камеры
camera_position = define_camera_place()

# Привязка нижней панели кнопок к функция
interface.buttonExit.clicked.connect(interface.close)
interface.homeButton.clicked.connect(set_home_position)
interface.cameraButton.clicked.connect(set_camera_position)
interface.runButton.clicked.connect(getting_started)

# Непосредственное управление роботом
QShortcut(QKeySequence("W"), interface).activated.connect(
    lambda: interface.keyboardControl('W'))
QShortcut(QKeySequence("A"), interface).activated.connect(
    lambda: interface.keyboardControl('A'))
QShortcut(QKeySequence("S"), interface).activated.connect(
    lambda: interface.keyboardControl('S'))
QShortcut(QKeySequence("D"), interface).activated.connect(
    lambda: interface.keyboardControl('D'))
QShortcut(QKeySequence("Space"), interface).activated.connect(
    lambda: interface.keyboardControl('Space'))
QShortcut(QKeySequence("C"), interface).activated.connect(
    lambda: interface.keyboardControl('C'))
QShortcut(QKeySequence("Q"), interface).activated.connect(
    lambda: interface.keyboardControl('Q'))
QShortcut(QKeySequence("E"), interface).activated.connect(
    lambda: interface.keyboardControl('E'))

# Кнопки захвата текущих координат робота и записи этих координат в entryfields
interface.buttonFurthest.clicked.connect(lambda: takeMyCurrentPoint(0))
interface.buttonNearest.clicked.connect(lambda: takeMyCurrentPoint(1))
interface.buttonNearest2.clicked.connect(lambda: takeMyCurrentPoint(2))
interface.buttonFurthest2.clicked.connect(lambda: takeMyCurrentPoint(3))


sys.exit(app.exec_())
