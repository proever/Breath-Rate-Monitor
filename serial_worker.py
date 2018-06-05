import serial
import numpy as np
import time

class SerialWorker:

    def __init__(self, port, lowerLim, upperLim, blockSize, blocks, baud):
        print('reading from serial port %s at %d baud...' % (port, baud))

        self.ser = self.serial_setup(port, lowerLim, upperLim, baud)
        self.zsize = 16384
        self.blockSize = blockSize
        self.blocks = blocks
        self.data = np.zeros((self.blocks, self.blockSize))
        self.publish_live_data = True

    def set_publish_live_data(self, publish_bool):
        self.publish_live_data = publish_bool

    def serial_setup(self, port, lowerLim, upperLim, baud):
        time.sleep(1)

        ser = serial.Serial(port, baud)

        ser.flushInput()
        # Incase flush leaves half a serial value
        ser.readline()

        return ser

    def live_data(self, EVT_ID, PostEvent, ResultEvent, wxObject):
        self.ser.flushInput()
        # Incase flush leaves half a serial value
        self.ser.readline()

        loop_count = 0
        while self.publish_live_data:
            if loop_count == self.blocks:
                loop_count = 0

            nums = np.zeros((self.blockSize))
            for i in range(self.blockSize):

                line = self.ser.readline()
                line = line.decode("utf-8")
                num = [float(val) for val in line.split()]

                try:
                    nums[i] = num[0]

                except IndexError:
                    pass

            self.data[loop_count] = nums

            loop_count += 1

            PostEvent(wxObject, ResultEvent(self.data, EVT_ID))

        self.ser.close()

    def stop(self):
        self.publish_live_data = False
