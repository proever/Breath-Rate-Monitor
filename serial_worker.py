import serial
import numpy as np
import time

class SerialWorker:

    def __init__(self):
        self.calibration_running = False
        self.calculation_running = False

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

    def calibrate(self, EVT_CALIBRATION_DATA_PUBLISHED, PostEvent, ResultEvent, wxObject, port, baud, blockSize, blocks):
        self.calibration_running = True

        ser = self.serial_setup(port, baud)
        ser.readline()

        data = np.zeros((blocks, blockSize))

        loop_count = 0
        while self.calibration_running:
            if loop_count == blocks:
                loop_count = 0

            nums = np.zeros((blockSize))
            for i in range(blockSize):

                line = ser.readline()
                line = line.decode("utf-8")
                num = [float(val) for val in line.split()]

                try:
                    nums[i] = num[0]

                except IndexError:
                    pass

            data[loop_count] = nums

            loop_count += 1

            PostEvent(wxObject, ResultEvent(data, EVT_CALIBRATION_DATA_PUBLISHED))

        ser.close()

    def calculate_BR(self, EVT_CALCULATION_PUBLISHED, PostEvent, ResultEvent, wxObject, port, baud, lowerLim, upperLim, view_time, yrange):
        self.calculation_running = True

        ser = self.serial_setup(port, baud)

        LED_state = 'Green'
        interval = 60
        pi = np.pi
        zdata = []
        zsize = 16384

        Breathing_rate_array = []
        time_array = []

        loop_count = 0
        interval_start = time.time()

        while self.calculation_running:
            if loop_count == 0:
                while time.time() <  interval + interval_start and self.calculation_running:
                        line = ser.readline()
                        line = line.decode("utf-8")
                        data = [float(val) for val in line.split()]
                        zdata.append(data)
            else:
                # determine data length corresponding to 15s
                del_length = round(zsize_init/4)
                # remove the first 15 seconds of data (so that we can append the next 15 seconds)
                del zdata[:del_length]
                while time.time() < interval_start + 15 and self.calculation_running:
                        line = ser.readline()
                        line = line.decode("utf-8")
                        data = [float(val) for val in line.split()]
                        zdata.append(data)

            # ensures 15 second intervals
            interval_start = time.time()
            # size before padding
            zsize_init = len(zdata)
            print(zsize_init)
            # pad width
            pad_width = 16384 - zsize_init
            #determine sampling frequency
            fs = zsize_init/interval
            # create array of zeros to pad
            pad_array = np.zeros(pad_width)
            # we do not want to alter the zdata (as 45 seconds will be used next cycle) therefore pad a copy
            zdata_copy = np.array(zdata,copy = True)
            # pad the copy
            padded_copy = np.append(zdata_copy,pad_array)
            # defines the "frequency axis" increment
            delta_f = fs/zsize
            # calulate fft of padded data
            zfft = np.fft.fft(padded_copy)
            zfft = np.abs(zfft)

            peak_max = 0;
            peakindex = 0;

            # peak finders (with "dynamic band pass filtering")
            if loop_count == 0:
                for x in range(np.ceil(0.6/delta_f).astype(np.int), np.ceil(1.3/delta_f).astype(np.int)): # 0.6 - 1.3 Hz initial search
                    if zfft[x] > peak_max:
                        peakindex = x
                        peak_max = zfft[x]
            else:
                for x in range(np.ceil((breathing_rate-0.15)/delta_f).astype(np.int), np.ceil((breathing_rate+0.15)/delta_f).astype(np.int)):
                    if zfft[x] > peak_max:
                        peakindex = x
                        peak_max = zfft[x]

            # determine breathing rate
            breathing_rate = delta_f * peakindex
            print(breathing_rate)
            print(time.time())
            # append to breathing rate array
            Breathing_rate_array.append(breathing_rate)

            time_array.append(0.25*loop_count)

            loop_count = loop_count + 1

            if loop_count > 40:
                plt.xlim([0.25*(loop_count-40),0.25*loop_count])


            if breathing_rate > lowerLim and breathing_rate < upperLim and LED_state != 'Green':
                LED_state = 'Green'
                ser.write(LED_state.encode())

            elif breathing_rate < lowerLim and LED_state != 'Low':
                LED_state = 'Low'
                ser.write(LED_state.encode())

            elif breathing_rate > upperLim and LED_state != 'High':
                LED_state = 'High'
                ser.write(LED_state.encode())

            data = (loop_count, time_array, Breathing_rate_array)
            PostEvent(wxObject, ResultEvent(data, EVT_CALCULATION_PUBLISHED))

    def stop(self):
        self.calibration_running = False
        self.calculation_running = False
        time.sleep(1)

