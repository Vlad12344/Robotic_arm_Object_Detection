# pip3 install pyFirmata2
# https://github.com/berndporr/pyFirmata2/tree/master/examples
# Example:
# laserread = LaserRead()
# laserread.start()
# while True:
#   if laserread.read() == 'True':
#       openCamera

from pyfirmata2 import Arduino

PORT = Arduino.AUTODETECT


class LaserRead:

    def __init__(self):
        self.samplingRate = 100
        self.timestamp = 0
        self.board = Arduino(PORT)
        self.digital_0 = self.board.get_pin('d:6:i')

    def start(self):
        self.board.samplingOn(1000 / self.samplingRate)
        self.digital_0.enable_reporting()

    def read(self):
        return self.digital_0.read()

    def stop(self):
        self.board.samplingOff()
        self.board.exit()
