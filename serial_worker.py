import serial
import numpy as np
import time

class SerialWorker:

    def __init__(self):
        self.zsize = 16384
        self.calibration_running = False

    def set_publish_live_data(self, publish_bool):
        self.calibration_running = publish_bool

    def serial_setup(self, port, baud):
        print('reading from serial port %s at %d baud...' % (port, baud))

        time.sleep(1)

        ser = serial.Serial(port, baud)

        ser.flushInput()
        # Incase flush leaves half a serial value
        ser.readline()

        return ser

    def calibrate(self, EVT_ID, PostEvent, ResultEvent, wxObject, port, blockSize, blocks, baud):
        self.ser = self.serial_setup(port, baud)
        self.calibration_running = True
        self.data = np.zeros((blocks, blockSize))

        time_till = time.time() + 60

        loop_count = 0
        while self.calibration_running and time.time() < time_till:
            if loop_count == blocks:
                loop_count = 0

            nums = np.zeros((blockSize))
            for i in range(blockSize):

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
        self.calibration_running = False
