from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
                             QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget, QFrame, QListWidget, QMessageBox, QShortcut)
from PyQt5.QtGui import QPainter, QPen, QKeySequence
from PyQt5.QtGui import QPalette, QColor
import sys

import numpy as np
from random import triangular, choice


class UI(QWidget):
    def __init__(self, app, parent=None):
        super(UI, self).__init__(parent)
        self.setGeometry(100, 200, 762, 438)
        self.setWindowTitle('Rozum Robotics Pulse 75')
        self.dark_theme(app)

        # Панель "Общие параметры"
        self.createCommonPanel()
        self.commonGroupBox.setParent(self)
        self.commonGroupBox.setGeometry(13, 28, 315, 122)

        # Панель "Параметры паллетирования"
        self.createPalletPanel()
        self.palletGroupBox.setParent(self)
        self.palletGroupBox.setGeometry(13, 209, 315, 139)
        self.palletGroupBox.setVisible(True)

        # Панель "Координаты областей раскладки"
        self.createZonesPanel()
        self.coordinatesGroupBox.setParent(self)
        self.coordinatesGroupBox.setGeometry(341, 28, 415, 320)

        # Панель "Раскладка по цветам"
        self.createColorPalletPanel()
        self.colorPalleteGroupBox.setParent(self)
        self.colorPalleteGroupBox.setGeometry(13, 209, 315, 139)

        # По умолчанию панель "Раскладка по цветам" выключена
        self.enableColorPalletising = QCheckBox("&Режим раскладки по цветам")
        self.enableColorPalletising.setChecked(False)
        self.enableColorPalletising.setParent(self)
        self.enableColorPalletising.clicked.connect(self.changeMode)
        self.enableColorPalletising.setGeometry(13, 160, 315, 50)
        self.colorPalleteGroupBox.setVisible(False)

        # Нижняя панель кнопок
        bottomLayout = QHBoxLayout()
        self.buttonExit = QPushButton('Выход')
        bottomLayout.addWidget(self.buttonExit)
        self.homeButton = QPushButton('Начальное положение')
        bottomLayout.addWidget(self.homeButton)
        self.cameraButton = QPushButton('Положение камеры')
        bottomLayout.addWidget(self.cameraButton)
        self.runButton = QPushButton('Запуск')
        bottomLayout.addWidget(self.runButton)
        bottomButtonsLayout = QVBoxLayout()
        bottomButtonsLayout.setContentsMargins(10, 10, 10, 20)
        bottomButtonsLayout.addStretch(1)
        bottomButtonsLayout.setSpacing(10)
        bottomButtonsLayout.addLayout(bottomLayout)
        self.setLayout(bottomButtonsLayout)

        # Чтение из файла и отображение сохранённых координат углов
        self.d = np.load('data/log/starting_coordinates.npy')
        self.entry_camera_x2.setText(str(round(self.d[0][0], 3)))
        self.entry_camera_y2.setText(str(round(self.d[0][1], 3)))
        self.entry_camera_z2.setText(str(round(self.d[0][2], 3)))
        self.entry_camera_x1.setText(str(round(self.d[1][0], 3)))
        self.entry_camera_y1.setText(str(round(self.d[1][1], 3)))
        self.entry_camera_z1.setText(str(round(self.d[1][2], 3)))
        self.entry_pallet_x2.setText(str(round(self.d[2][0], 3)))
        self.entry_pallet_y2.setText(str(round(self.d[2][1], 3)))
        self.entry_pallet_z2.setText(str(round(self.d[2][2], 3)))
        self.entry_pallet_x1.setText(str(round(self.d[3][0], 3)))
        self.entry_pallet_y1.setText(str(round(self.d[3][1], 3)))
        self.entry_pallet_z1.setText(str(round(self.d[3][2], 3)))

        self.entrySize.setText('0.05')
        self.entryBetween.setText('0.01')
        self.autoColors()

        # Словарь цветов
        self.PALLET_LIST = {}

    def dark_theme(self, app):
        app.setStyle("Fusion")
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(dark_palette)
        app.setStyleSheet(
            "QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    def createCommonPanel(self):
        self.commonGroupBox = QGroupBox('Общие параметры')
        commonLayout = QVBoxLayout()

        line1 = QHBoxLayout()
        labelSpeed = QLabel('Скорость работы')
        labelSpeed.setFixedWidth(275)
        line1.addWidget(labelSpeed)
        self.comboSpeed = QComboBox()
        self.comboSpeed.setFixedWidth(50)
        self.comboSpeed.addItems(['5', '10', '15', '20', '30', '40', '100'])
        self.comboSpeed.setCurrentIndex(3)
        line1.addWidget(self.comboSpeed)
        line1.addStretch(1)
        commonLayout.addLayout(line1)

        line2 = QHBoxLayout()
        labelSize = QLabel('Размер детали')
        labelSize.setFixedWidth(275)
        line2.addWidget(labelSize)
        self.entrySize = QLineEdit()
        self.entrySize.setFixedWidth(50)
        line2.addWidget(self.entrySize)
        line2.addStretch(1)
        commonLayout.addLayout(line2)

        line3 = QHBoxLayout()
        labelBetween = QLabel('Расстояние между деталями')
        labelBetween.setFixedWidth(275)
        line3.addWidget(labelBetween)
        self.entryBetween = QLineEdit()
        self.entryBetween.setFixedWidth(50)
        line3.addWidget(self.entryBetween)
        line3.addStretch(1)
        commonLayout.addLayout(line3)

        self.commonGroupBox.setLayout(commonLayout)

    def createPalletPanel(self):
        self.palletGroupBox = QGroupBox('Паллетирование')
        self.palletGroupBox.setFixedSize(315, 139)

        palletLayout = QVBoxLayout()

        line1 = QHBoxLayout()
        line1.addWidget(QLabel('Высота паллеты'))
        self.comboHeightPallet = QComboBox()
        self.comboHeightPallet.setFixedWidth(100)
        self.comboHeightPallet.addItems(
            ['1', '2', '3', '4', '5'])
        line1.addWidget(self.comboHeightPallet)
        palletLayout.addLayout(line1)

        line2 = QHBoxLayout()
        line2.addWidget(QLabel('Ширина паллеты'))
        self.comboWidthPallet = QComboBox()
        self.comboWidthPallet.setFixedWidth(100)
        self.comboWidthPallet.addItems(
            ['1', '2', '3', '4', '5'])
        line2.addWidget(self.comboWidthPallet)
        palletLayout.addLayout(line2)

        line3 = QHBoxLayout()
        self.enableAllDetails = QCheckBox("&Списком")
        line3.addWidget(self.enableAllDetails)
        self.enableAllDetails.setChecked(False)
        palletLayout.addLayout(line3)

        self.palletGroupBox.setLayout(palletLayout)

    def createColorPalletPanel(self):
        self.colorPalleteGroupBox = QGroupBox('Раскладка по цветам')
        self.colorPalleteGroupBox.setFixedSize(315, 139)

        line1 = QHBoxLayout()
        self.listboxColorOrder = QListWidget()
        self.listColors = ['1', '3', '4', '5']
        self.listboxColorOrder.addItems(self.listColors)
        self.listboxColorOrder.setFixedWidth(130)
        line1.addWidget(self.listboxColorOrder)

        line2 = QVBoxLayout()
        line1.addLayout(line2)
        buttonUp = QPushButton('Вверх')
        buttonUp.clicked.connect(self.moveItemUp)

        line2.addWidget(buttonUp)
        buttonDown = QPushButton('Вниз')
        buttonDown.clicked.connect(self.moveItemDown)
        line2.addWidget(buttonDown)
        self.enableAutoColors = QCheckBox('Автоматически')
        self.enableAutoColors.setChecked(True)
        self.enableAutoColors.toggled.connect(self.autoColors)
        line2.addWidget(self.enableAutoColors)

        self.colorPalleteGroupBox.setLayout(line1)

    def createZonesPanel(self):
        self.coordinatesGroupBox = QGroupBox('Координаты углов рабочих областей')
        self.coordinatesGroupBox.setFixedSize(415, 320)

        coordinatesLayout = QVBoxLayout()

        pointsLayout1 = QHBoxLayout()
        pointsLayout1.addWidget(QLabel('Координаты углов области камеры'))
        pointsLayout1.addStretch(1)

        pointsLayout2 = QHBoxLayout()
        pointsLayout2.setSpacing(7)
        cornerLabel1 = QLabel('Дальний:')
        cornerLabel1.setFixedWidth(90)
        pointsLayout2.addWidget(cornerLabel1)
        pointsLayout2.addWidget(QLabel('x'))
        self.entry_camera_x2 = QLineEdit()
        pointsLayout2.addWidget(self.entry_camera_x2)
        pointsLayout2.addWidget(QLabel('y'))
        self.entry_camera_y2 = QLineEdit()
        pointsLayout2.addWidget(self.entry_camera_y2)
        pointsLayout2.addWidget(QLabel('z'))
        self.entry_camera_z2 = QLineEdit()
        pointsLayout2.addWidget(self.entry_camera_z2)
        self.buttonFurthest = QPushButton('Захватить')
        pointsLayout2.addWidget(self.buttonFurthest)

        pointsLayout3 = QHBoxLayout()
        pointsLayout3.setSpacing(7)
        cornerLabel2 = QLabel('Ближний:')
        cornerLabel2.setFixedWidth(90)
        pointsLayout3.addWidget(cornerLabel2)
        pointsLayout3.addWidget(QLabel('x'))
        self.entry_camera_x1 = QLineEdit()
        pointsLayout3.addWidget(self.entry_camera_x1)
        pointsLayout3.addWidget(QLabel('y'))
        self.entry_camera_y1 = QLineEdit()
        pointsLayout3.addWidget(self.entry_camera_y1)
        pointsLayout3.addWidget(QLabel('z'))
        self.entry_camera_z1 = QLineEdit()
        pointsLayout3.addWidget(self.entry_camera_z1)
        self.buttonNearest = QPushButton('Захватить')
        pointsLayout3.addWidget(self.buttonNearest)

        pointsLayout4 = QHBoxLayout()
        pointsLayout4.addStretch()
        buttonEdit = QPushButton('Изменить')
        buttonSave = QPushButton('Сохранить')
        pointsLayout4.addWidget(buttonEdit)
        pointsLayout4.addWidget(buttonSave)

        self.entry_camera_x2.setDisabled(True)
        self.entry_camera_y2.setDisabled(True)
        self.entry_camera_z2.setDisabled(True)
        self.entry_camera_x1.setDisabled(True)
        self.entry_camera_y1.setDisabled(True)
        self.entry_camera_z1.setDisabled(True)

        pointsLayout5 = QHBoxLayout()
        pointsLayout5.addWidget(QLabel('Координаты углов области раскладки'))
        pointsLayout5.addStretch(1)

        pointsLayout6 = QHBoxLayout()
        pointsLayout6.setSpacing(7)
        cornerLabel = QLabel('Дальний:')
        cornerLabel.setFixedWidth(90)
        pointsLayout6.addWidget(cornerLabel)
        pointsLayout6.addWidget(QLabel('x'))
        self.entry_pallet_x2 = QLineEdit()
        pointsLayout6.addWidget(self.entry_pallet_x2)
        pointsLayout6.addWidget(QLabel('y'))
        self.entry_pallet_y2 = QLineEdit()
        pointsLayout6.addWidget(self.entry_pallet_y2)
        pointsLayout6.addWidget(QLabel('z'))
        self.entry_pallet_z2 = QLineEdit()
        pointsLayout6.addWidget(self.entry_pallet_z2)
        self.buttonNearest2 = QPushButton('Захватить')
        pointsLayout6.addWidget(self.buttonNearest2)

        pointsLayout7 = QHBoxLayout()
        pointsLayout7.setSpacing(7)
        cornerLabel2 = QLabel('Ближний:')
        cornerLabel2.setFixedWidth(90)
        pointsLayout7.addWidget(cornerLabel2)
        pointsLayout7.addWidget(QLabel('x'))
        self.entry_pallet_x1 = QLineEdit()
        pointsLayout7.addWidget(self.entry_pallet_x1)
        pointsLayout7.addWidget(QLabel('y'))
        self.entry_pallet_y1 = QLineEdit()
        pointsLayout7.addWidget(self.entry_pallet_y1)
        pointsLayout7.addWidget(QLabel('z'))
        self.entry_pallet_z1 = QLineEdit()
        pointsLayout7.addWidget(self.entry_pallet_z1)
        self.buttonFurthest2 = QPushButton('Захватить')
        pointsLayout7.addWidget(self.buttonFurthest2)

        self.entry_pallet_x2.setDisabled(True)
        self.entry_pallet_y2.setDisabled(True)
        self.entry_pallet_z2.setDisabled(True)
        self.entry_pallet_x1.setDisabled(True)
        self.entry_pallet_y1.setDisabled(True)
        self.entry_pallet_z1.setDisabled(True)

        pointsLayout8 = QHBoxLayout()
        pointsLayout8.addStretch()
        buttonEdit2 = QPushButton('Изменить')
        buttonSave2 = QPushButton('Сохранить')

        pointsLayout8.addWidget(buttonEdit2)
        pointsLayout8.addWidget(buttonSave2)

        coordinatesLayout.addLayout(pointsLayout1)
        coordinatesLayout.addLayout(pointsLayout2)
        coordinatesLayout.addLayout(pointsLayout3)
        coordinatesLayout.addLayout(pointsLayout4)
        coordinatesLayout.addLayout(pointsLayout5)
        coordinatesLayout.addLayout(pointsLayout6)
        coordinatesLayout.addLayout(pointsLayout7)
        coordinatesLayout.addLayout(pointsLayout8)

        coordinatesLayout.setSpacing(15)

        self.coordinatesGroupBox.setLayout(coordinatesLayout)

        # Кнопки в панели задания координат
        buttonEdit.clicked.connect(lambda: self.editCoordinates('change_camera'))
        buttonSave.clicked.connect(lambda: self.editCoordinates('save_camera'))
        buttonEdit2.clicked.connect(lambda: self.editCoordinates('change_pallet'))
        buttonSave2.clicked.connect(lambda: self.editCoordinates('save_pallet'))

    def changeMode(self):
        if self.enableColorPalletising.isChecked():
            self.palletGroupBox.setVisible(False)
            self.colorPalleteGroupBox.setVisible(True)
        else:
            self.colorPalleteGroupBox.setVisible(False)
            self.palletGroupBox.setVisible(True)

    def moveItemUp(self):
        currentRow = self.listboxColorOrder.currentRow()
        currentItem = self.listboxColorOrder.takeItem(currentRow)
        self.listboxColorOrder.insertItem(currentRow - 1, currentItem)
        self.listboxColorOrder.setCurrentRow(currentRow - 1)

    def moveItemDown(self):
        currentRow = self.listboxColorOrder.currentRow()
        currentItem = self.listboxColorOrder.takeItem(currentRow)
        self.listboxColorOrder.insertItem(currentRow + 1, currentItem)
        self.listboxColorOrder.setCurrentRow(currentRow + 1)

    def autoColors(self):
        if self.enableAutoColors.isChecked():
            self.listboxColorOrder.setDisabled(True)
            self.PALLET_LIST = {}
        else:
            self.listboxColorOrder.setDisabled(False)
            colors = []
            for color in range(self.listboxColorOrder.count()):
                colors.append(self.listboxColorOrder.item(color).text())
            values = []
            for i in range(len(colors)):
                values.append([])
            self.PALLET_LIST = dict(zip(colors, values))

    def editCoordinates(self, state):
        if state == 'change_camera':
            self.entry_camera_x2.setDisabled(False)
            self.entry_camera_y2.setDisabled(False)
            self.entry_camera_z2.setDisabled(False)
            self.entry_camera_x1.setDisabled(False)
            self.entry_camera_y1.setDisabled(False)
            self.entry_camera_z1.setDisabled(False)
        if state == 'save_camera':
            self.d[0] = [str(self.entry_camera_x2.text()),
                         str(self.entry_camera_y2.text()),
                         str(self.entry_camera_z2.text())]
            self.d[1] = [str(self.entry_camera_x1.text()),
                         str(self.entry_camera_y1.text()),
                         str(self.entry_camera_z1.text())]
            np.save('data/log/starting_coordinates.npy', self.d)
            self.entry_camera_x1.setDisabled(True)
            self.entry_camera_y1.setDisabled(True)
            self.entry_camera_z1.setDisabled(True)
            self.entry_camera_x2.setDisabled(True)
            self.entry_camera_y2.setDisabled(True)
            self.entry_camera_z2.setDisabled(True)
        if state == 'change_pallet':
            self.entry_pallet_x1.setDisabled(False)
            self.entry_pallet_y1.setDisabled(False)
            self.entry_pallet_z1.setDisabled(False)
            self.entry_pallet_x2.setDisabled(False)
            self.entry_pallet_y2.setDisabled(False)
            self.entry_pallet_z2.setDisabled(False)
        if state == 'save_pallet':
            self.d[2] = [str(self.entry_pallet_x2.text()),
                         str(self.entry_pallet_y2.text()),
                         str(self.entry_pallet_z2.text())]
            self.d[3] = [str(self.entry_pallet_x1.text()),
                         str(self.entry_pallet_y1.text()),
                         str(self.entry_pallet_z2.text())]
            np.save('data/log/starting_coordinates.npy', self.d)
            self.entry_pallet_x1.setDisabled(True)
            self.entry_pallet_y1.setDisabled(True)
            self.entry_pallet_z1.setDisabled(True)
            self.entry_pallet_x2.setDisabled(True)
            self.entry_pallet_y2.setDisabled(True)
            self.entry_pallet_z2.setDisabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    interface = UI(app)
    interface.show()
    sys.exit(app.exec_())
