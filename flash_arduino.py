from sys import platform
import os
from subprocess import check_output

def main(port):
    if platform == "win32":
        print("on Windows, proceeding...")

        # TODO: revert to . not ..
        exe_fp = os.path.join("..", "arduino-1.8.5", "arduino_debug.exe")
        board = "arduino:avr:uno"
        sketch_fp = os.path.join(".", "arduino_code", "serial_interface.ino")

        arg = exe_fp + " --board " + board + " --port " + port + " --upload " + sketch_fp

        print(arg)

        return check_output(arg)

    else:
        print("error, on " + platform + ", not Windows")

