from sys import platform
import os
from subprocess import check_output

def main(port):
    if platform == "win32":
        print("on Windows, proceeding...")

        exe_fp = os.path.join(".", "arduino-1.8.5", "arduino_debug.exe")
        if not os.path.exists(exe_fp):
            exe_fp = os.path.join("..", "arduino-1.8.5", "arduino_debug.exe")
            if not os.path.exists(exe_fp):
                return 1

        board = "arduino:avr:uno"
        sketch_fp = os.path.join(".", "arduino_code", "serial_interface.ino")

        command = exe_fp + " --board " + board + " --port " + port + " --upload " + sketch_fp

        print(command)

        return check_output(command)

    else:
        print("error, on " + platform + ", not Windows")

