#TODO: force folder choice here
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.8.2 on Sat Jun  2 15:02:51 2018
#

import wx
from subprocess import check_output
import datetime
import os
from threading import Thread
import time
import numpy as np
import matplotlib
matplotlib.use('wxAgg')
import matplotlib.pyplot as plt

from list_ports import serial_ports
import flash_arduino
from serial_worker import SerialWorker
# import calibrate

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade

EVT_CALCULATION_PUBLISHED = wx.NewId()
EVT_CALIBRATION_DATA_PUBLISHED = wx.NewId()

def bind_EVT(win, func, EVT_ID):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data, EVT_ID):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_ID)
        self.data = data

class CalculationThread(Thread):
    """Test Worker Thread Class."""

    #----------------------------------------------------------------------
    def __init__(self, wxObject, port, lowerLim, upperLim, view_time, yrange, baud=4800):
        """Init Worker Thread Class."""
        Thread.__init__(self)

        self.port = port
        self.baud = baud
        self.lowerLim = lowerLim
        self.upperLim = upperLim
        self.view_time = view_time
        self.yrange = yrange

        self.serialWorker = SerialWorker()
        self.wxObject = wxObject
        self.daemon = True
        self.start()    # start the thread

    #----------------------------------------------------------------------
    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread.
        self.serialWorker.calculate_BR(EVT_CALCULATION_PUBLISHED, wx.PostEvent, ResultEvent, self.wxObject, self.port, self.baud, self.lowerLim, self.upperLim, self.view_time, self.yrange)

class CalibrationThread(Thread):
    """Test Worker Thread Class."""

    #----------------------------------------------------------------------
    def __init__(self, wxObject, port, blockSize, blocks, baud=4800):
        """Init Worker Thread Class."""
        Thread.__init__(self)

        self.port = port
        self.baud = baud
        self.blockSize = blockSize
        self.blocks = blocks

        self.serialWorker = SerialWorker()
        self.wxObject = wxObject
        self.daemon = True
        self.start()    # start the thread

    #----------------------------------------------------------------------
    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread.
        self.serialWorker.calibrate(EVT_CALIBRATION_DATA_PUBLISHED, wx.PostEvent, ResultEvent, self.wxObject, self.port, self.baud, self.blockSize, self.blocks)


class BreathRateMonitorWindow(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: BreathRateMonitorWindow.__init__
        self.port = None
        self.calibrationThread = None
        self.calculationThread = None

        self.lowerLim = 0.75
        self.upperLim = 1.25
        self.blockSize = 10
        self.blocks = 100
        self.view_time = 10 # minutes
        self.yrange = [-0.1, 1.5]

        self.path = None
        self.filename = None

        self.f = None

        plt.ion()

        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((600, 350))
        # Menu Bar
        self.imagingSetup_menubar = wx.MenuBar()
        self.SetMenuBar(self.imagingSetup_menubar)
        # Menu Bar end
        self.main_panel = wx.Panel(self, wx.ID_ANY)
        self.refresh_btn = wx.Button(self.main_panel, wx.ID_ANY, "Refresh")
        self.port_choice = wx.Choice(self.main_panel, wx.ID_ANY, choices=ports)
        self.build_btn = wx.Button(self.main_panel, wx.ID_ANY, "Build")
        self.calibrate_btn = wx.Button(self.main_panel, wx.ID_ANY, "Calibrate")
        self.lowerThreshold_spinDouble = wx.SpinCtrlDouble(self.main_panel, wx.ID_ANY,str(self.lowerLim), min=0.0, max=1.01)
        self.upperThreshold_spinDouble = wx.SpinCtrlDouble(self.main_panel, wx.ID_ANY,str(self.upperLim), min=0.99, max=3.0)
        self.saveToFolder_checkbox = wx.CheckBox(self.main_panel, wx.ID_ANY, "")
        self.folderPath_field = wx.TextCtrl(self.main_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL | wx.TE_READONLY)
        self.chooseFolder_btn = wx.Button(self.main_panel, wx.ID_ANY, "Choose a folder")
        self.start_btn = wx.Button(self.main_panel, wx.ID_ANY, "Start Imaging")
        self.quit_btn = wx.Button(self.main_panel, wx.ID_ANY, "Quit")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.refresh_ports, self.refresh_btn)
        self.Bind(wx.EVT_CHOICE, self.update_port, self.port_choice)
        self.Bind(wx.EVT_BUTTON, self.build, self.build_btn)
        self.Bind(wx.EVT_BUTTON, self.calibrate, self.calibrate_btn)
        self.Bind(wx.EVT_CHECKBOX, self.update_filename, self.saveToFolder_checkbox)
        self.Bind(wx.EVT_BUTTON, self.folder_picker, self.chooseFolder_btn)
        self.Bind(wx.EVT_BUTTON, self.startImaging, self.start_btn)
        self.Bind(wx.EVT_BUTTON, self.quit, self.quit_btn)
        # end wxGlade

        self.lowerThreshold_spinDouble.SetIncrement(0.01)
        self.upperThreshold_spinDouble.SetIncrement(0.01)

        self.Bind(wx.EVT_CLOSE, self.on_close)
        bind_EVT(self, self.update_calibration_plot, EVT_CALIBRATION_DATA_PUBLISHED)
        bind_EVT(self, self.update_calculation_plot, EVT_CALCULATION_PUBLISHED)

    def __set_properties(self):
        # begin wxGlade: BreathRateMonitorWindow.__set_properties
        self.SetTitle("Breath Rate Monitor: Set Up Session")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: BreathRateMonitorWindow.__do_layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        rows_sizer = wx.BoxSizer(wx.VERTICAL)
        startQuit_sizer = wx.BoxSizer(wx.HORIZONTAL)
        saveToFolder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        alerts_sizer = wx.BoxSizer(wx.HORIZONTAL)
        upperAlert_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lowerAlert_sizer = wx.BoxSizer(wx.HORIZONTAL)
        imagingOptions_sizer = wx.BoxSizer(wx.HORIZONTAL)
        calibrate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        port_sizer = wx.BoxSizer(wx.HORIZONTAL)
        portSelectBuild_text = wx.StaticText(self.main_panel, wx.ID_ANY, "Please select a port and then press build")
        port_sizer.Add(portSelectBuild_text, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        port_sizer.Add(self.refresh_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        port_sizer.Add(self.port_choice, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        port_sizer.Add(self.build_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        rows_sizer.Add(port_sizer, 1, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5)
        welcomeCalibrate_text = wx.StaticText(self.main_panel, wx.ID_ANY, "Calibrate if necessary:")
        calibrate_sizer.Add(welcomeCalibrate_text, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        calibrate_sizer.Add(self.calibrate_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        rows_sizer.Add(calibrate_sizer, 1, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5)
        imagingOptions = wx.StaticText(self.main_panel, wx.ID_ANY, "Imaging options below:")
        imagingOptions_sizer.Add(imagingOptions, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        rows_sizer.Add(imagingOptions_sizer, 1, wx.ALL, 5)
        alertThresholds_text = wx.StaticText(self.main_panel, wx.ID_ANY, "Alert thresholds (breaths/sec):")
        alerts_sizer.Add(alertThresholds_text, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        lower_text = wx.StaticText(self.main_panel, wx.ID_ANY, "Lower:")
        lowerAlert_sizer.Add(lower_text, 0, wx.ALIGN_CENTER, 0)
        lowerAlert_sizer.Add(self.lowerThreshold_spinDouble, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        alerts_sizer.Add(lowerAlert_sizer, 1, wx.ALIGN_CENTER, 5)
        alerts_sizer.Add((20, 0), 0, 0, 0)
        upper_text = wx.StaticText(self.main_panel, wx.ID_ANY, "Upper:")
        upperAlert_sizer.Add(upper_text, 0, wx.ALIGN_CENTER, 0)
        upperAlert_sizer.Add(self.upperThreshold_spinDouble, 0, 0, 0)
        alerts_sizer.Add(upperAlert_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 0)
        rows_sizer.Add(alerts_sizer, 1, wx.ALL, 5)
        saveToFolder_sizer.Add(self.saveToFolder_checkbox, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        saveToFolder_text = wx.StaticText(self.main_panel, wx.ID_ANY, "save to file: ")
        saveToFolder_sizer.Add(saveToFolder_text, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        saveToFolder_sizer.Add(self.folderPath_field, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        saveToFolder_sizer.Add(self.chooseFolder_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        rows_sizer.Add(saveToFolder_sizer, 1, wx.ALL | wx.EXPAND, 5)
        startQuit_sizer.Add(self.start_btn, 0, wx.ALIGN_CENTER | wx.ALIGN_RIGHT | wx.ALL, 5)
        startQuit_sizer.Add(self.quit_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        rows_sizer.Add(startQuit_sizer, 1, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER | wx.ALIGN_RIGHT | wx.ALL, 5)
        self.main_panel.SetSizer(rows_sizer)
        main_sizer.Add(self.main_panel, 0, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(main_sizer)
        self.Layout()
        # end wxGlade

    def refresh_ports(self, event):  # wxGlade: BreathRateMonitorWindow.<event_handler>
        ports = serial_ports()
        self.port_choice.Clear()
        self.port_choice.Append(ports)

    def update_port(self, event):  # wxGlade: BreathRateMonitorWindow.<event_handler>
        portIndex = self.port_choice.GetSelection()
        self.port = self.port_choice.GetString(portIndex)

    def update_filename(self, event):
        if self.saveToFolder_checkbox.GetValue() and self.path == None:
            self.folder_picker(event)

    def build(self, event):  # wxGlade: BreathRateMonitorWindow.<event_handler>
        if self.port == None:
            self.noPortMsg()
        else:
            #TODO: turn this and others into confirm/cancel box with consequences
            wx.MessageBox('Flashing board, please wait', 'Info', wx.OK | wx.ICON_INFORMATION)
            res = flash_arduino.main(self.port)
            print("Done")

    # def begin_live_data_gen(self, event):
    #     wx.MessageBox('Data generation started', 'Info',
    #             wx.OK | wx.ICON_INFORMATION)
    #     self.calibrationThread = CalibrationThread(self, self.port, self.lowerLim, self.upperLim, self.blockSize, self.blocks)

    def start_calculation_plot(self, event):
        self.calculation_fig = plt.figure()
        self.calculation_fig.canvas.mpl_connect('close_event', self.handle_fig_close)
        self.calculation_fig.patch.set_facecolor((0.05,0.05,0.05))
        self.calculation_fig.suptitle('Breathing rate data',fontsize = '18', fontweight = 'bold',color = 'white')
        plt.xlabel('time, mins', fontsize='14', fontstyle='italic',color = 'white')
        plt.gca().grid(True)
        self.calculation_line, = plt.plot([],marker='o',markersize=4,markerfacecolor='red')
        plt.ylim(self.yrange)
        plt.xlim([0, self.view_time])
        ax = plt.gca()
        ax.set_facecolor((0.1,0.1,0.1))
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

    def start_calibration_plot(self, event):
        self.calibration_fig = plt.figure()
        self.calibration_fig.canvas.mpl_connect('close_event', self.handle_fig_close)
        plt.plot(np.zeros(100*10))

    def handle_fig_close(self, event):
        self.stop_serialThread(event)
        print ('Closed Figure')

        #update filename to create new file on next session
        if self.saveToFolder_checkbox.GetValue() and self.path != None:
            st = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
            self.filename = "FILM_session_" + st + ".csv"
            self.folderPath_field.write(os.path.join(self.path, self.filename))

    def update_calculation_plot(self, event):
        if plt.get_fignums():
            loop_count = event.data[0]
            time_array = event.data[1]
            Breathing_rate_array = event.data[2]

            if loop_count > 40:
                ax = plt.gca()
                ax.set_xlim([0.25*(loop_count-40),0.25*loop_count])

            self.calculation_line.set_xdata(time_array)
            self.calculation_line.set_ydata(Breathing_rate_array)

            self.calculation_fig.canvas.draw()

            if self.saveToFolder_checkbox.GetValue() and self.path != None:
                if self.f != None:
                    st = datetime.datetime.now().strftime('%H:%M:%S')
                    line = st + "," + str(Breathing_rate_array[-1]) + "\n"
                    self.f.write(line)

    def update_calibration_plot(self, event):
        if plt.get_fignums():
            nums = np.reshape(event.data,(100*10))
            plt.cla()
            plt.plot(nums)

    def calibrate(self, event):  # wxGlade: BreathRateMonitorWindow.<event_handler>
        if self.port == None:
            self.noPortMsg()

        elif self.calculationThread != None and self.calculationThread.isAlive():
            wx.MessageBox('BR calculation is in progress, please close that window before calibrating', 'Error', wx.OK | wx.ICON_INFORMATION)

        elif self.calibrationThread == None:
            wx.MessageBox('Starting calibration...', 'Info', wx.OK | wx.ICON_INFORMATION)
            self.calibrationThread = CalibrationThread(self, self.port, self.blockSize, self.blocks)
            self.start_calibration_plot(event)

        elif self.calibrationThread.isAlive():
            #TODO: bring window to foreground?
            pass

        else:
            wx.MessageBox('Starting calibration...', 'Info', wx.OK | wx.ICON_INFORMATION)
            self.calibrationThread = CalibrationThread(self, self.port, self.blockSize, self.blocks)
            self.start_calibration_plot(event)

    def folder_picker(self, event):  # wxGlade: BreathRateMonitorWindow.<event_handler>
        self.saveToFolder_checkbox.SetValue(True)
        self.folderPath_field.Clear()
        st = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
        self.filename = "FILM_session_" + st + ".csv"

        folder_dlg = wx.DirDialog(None, "Choose a folder", "",
                wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

        try:
            if folder_dlg.ShowModal() == wx.ID_CANCEL:
                return
            self.path = folder_dlg.GetPath()
            self.folderPath_field.write(os.path.join(self.path, self.filename))
        except Exception:
            wx.LogError('Failed to open directory!')
            raise
        finally:
            folder_dlg.Destroy()

    def check_fp_and_start_threads(self, event):
        #TODO: force folder choice here
        if self.saveToFolder_checkbox.GetValue() and self.path == None:
            self.folder_picker(event)

        filepath = os.path.join(self.path, self.filename)
        self.f = open(filepath, "w")

        wx.MessageBox('Starting calculation...', 'Info', wx.OK | wx.ICON_INFORMATION)
        self.calculationThread = CalculationThread(self, self.port, self.lowerLim, self.upperLim, self.view_time, self.yrange)
        self.start_calculation_plot(event)

    def startImaging(self, event):  # wxGlade: BreathRateMonitorWindow.<event_handler>
        if self.port == None:
            self.noPortMsg()

        elif self.calibrationThread != None and self.calibrationThread.isAlive():
            wx.MessageBox('BR calibration is in progress, please close that window before starting the calculation', 'Error', wx.OK | wx.ICON_INFORMATION)

        elif self.calculationThread == None:
            self.check_fp_and_start_threads(event)

        elif self.calculationThread.isAlive():
            #TODO: bring window to foreground?
            pass

        else:
            self.check_fp_and_start_threads(event)

    def quit(self, event):  # wxGlade: BreathRateMonitorWindow.<event_handler>
        self.on_close(event)

    def on_close(self, event):
        plt.close("all")
        self.stop_serialThread(event)

        time.sleep(0.5)

        if self.f != None:
            self.f.close()

        self.Destroy()

    def stop_serialThread(self, event):
        if self.calculationThread != None and self.calculationThread.isAlive():
            self.calculationThread.serialWorker.stop()
            print("Terminated Calculation Thread")

        if self.calibrationThread != None and self.calibrationThread.isAlive():
            self.calibrationThread.serialWorker.stop()
            print("Terminated Calibration Thread")

    def noPortMsg(self):
        wx.MessageBox('Please select a port', 'Error',
                wx.OK | wx.ICON_INFORMATION)


# end of class BreathRateMonitorWindow

class BreathRateMonitorSetup(wx.App):
    def OnInit(self):
        self.imagingSetup = BreathRateMonitorWindow(None, wx.ID_ANY, "")
        self.SetTopWindow(self.imagingSetup)
        self.imagingSetup.Show()
        return True

# end of class BreathRateMonitorSetup

if __name__ == "__main__":
    ports = serial_ports()
    breathRateMonitorSetup = BreathRateMonitorSetup(0, ports)
    breathRateMonitorSetup.MainLoop()

