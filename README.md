# Breath-Rate-Monitor

## Installation Instructions
- build gui.py with PyInstaller on Windows.
- copy arduino_code to dist/gui
- download the non-admin [version](https://www.arduino.cc/download_handler.php?f=/arduino-1.8.5-windows.zip) of the Arduino library as a ZIP file (tested with 1.8.5, should remain compatible) and extract it to dist/gui

Folder hierarchy should look as follows:

```
\ --- Breath-Rate-Monitor
      |
      |
      \ --- dist
            |
            |
            \ --- gui
                  |
                  | --- gui.exe
                  |
                  \ --- arduino_code
                  |     |
                  |     | --- serial_interface.ino
                  |
                  \ --- arduino-1.8.5
```

## To Run
- open gui.exe (can have a shortcut on the desktop)
- choose the correct port (disconnect and refresh, then connect and refresh if not sure)
- select build
- select calibrate when finished to ensure correct sensor positioning (spikes should be large (~ 8 - 12) and distinct)
- close the calibration window
- select the upper and lower thresholds of the breathing rate at which you would like to be notified
- check save to file if you want to keep a log of the estimated breathing rate at 15-second intervals
- select the folder to save the logs in (files are automatically called FILM_session_{year}-{month}-{day}_{hour}-{minute}.csv)
- select Start Imaging to open the live view of the estimated breathing rate (it will take one minute initially to generate an estimate)
- close the live view when you have finished the imaging session, this also saves the generated data (it will not be available before this time)
