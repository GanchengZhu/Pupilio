import serial

from pupilio.callback import CalibrationListener
from uservo import UartServoManager

"""
请参考`my_calibration_listener.py`这个文件
"""

class UservoListener(CalibrationListener):
    def __init__(self):
        self.port = 'COM3'
        self.baudrate = 115200
        self.uart = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            parity=serial.PARITY_NONE,
            stopbits=1,
            bytesize=8,
            timeout=0)

        self.uservo = UartServoManager(self.uart, is_debug=True)

    def on_calibration_target_over(self):
        angle = [-56, 0, -7, 6]
        for i in range(4):
            self.send_angle_command(i, angle[i])

    def on_calibration_target_onset(self, point_index):
        if point_index == 0:
            angle = [-56, -9, -7, 0]
            for i in range(4):
                self.send_angle_command(i, angle[i])
        elif point_index == 1:
            angle = [-56, 9, -7, 12]
            for i in range(4):
                self.send_angle_command(i, angle[i])

    def send_angle_command(self, servo_id, angle):
        """control the servo motor to change the gaze direction"""
        self.uservo.set_servo_angle(servo_id, angle, interval=100)
        self.uservo.wait()

