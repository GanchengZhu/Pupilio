# _*_ coding: utf-8 _*_
# Author: GC Zhu
# Email: zhugc2016@gmail.com
import os
from .misc import CalibrationMode


class DefaultConfig:
    """
    Default configuration class containing various parameters required for program execution.
    Includes settings for file paths, hyperparameters, and resources like images and audio.
    """

    def __init__(self):
        # Get the absolute path of the current file's directory
        self._current_dir = os.path.abspath(os.path.dirname(__file__))

        # Filter hyperparameters
        self.look_ahead = 2  # Look-ahead steps for predicting target position

        # Font settings
        # self.font_name = "Microsoft YaHei UI"  # Font used for displaying text

        # Calibration resource file paths
        # Sound file for target beep during calibration
        self.cali_target_beep = os.path.join(self._current_dir, "asset",
                                             "beep.wav")  # Path to the calibration target beep sound

        # Calibration face images
        self.cali_frowning_face_img = os.path.join(self._current_dir, "asset",
                                                   "frowning-face.png")  # Path to frowning face image
        self.cali_smiling_face_img = os.path.join(self._current_dir, "asset",
                                                  "smiling-face.png")  # Path to smiling face image

        # Calibration target image
        self.cali_target_img = os.path.join(self._current_dir, "asset",
                                            "windmill.png")  # Path to windmill image used as calibration target

        # Calibration target image size limits
        self.cali_target_img_maximum_size = 60  # Maximum size of the calibration target image
        self.cali_target_img_minimum_size = 30  # Minimum size of the calibration target image

        # Calibration target animation frequency
        self.cali_target_animation_frequency = 2  # Frequency of the calibration target animation (in Hz)

        # Calibration mode (either 2 or 5)
        self.cali_mode = CalibrationMode.TWO_POINTS  # Default to TWO_POINTS calibration mode

    @property
    def cali_mode(self):
        return self._cali_mode

    @cali_mode.setter
    def cali_mode(self, mode):
        if isinstance(mode, CalibrationMode):
            self._cali_mode = mode
        elif mode == 2:
            self._cali_mode = CalibrationMode.TWO_POINTS
        elif mode == 5:
            self._cali_mode = CalibrationMode.FIVE_POINTS  # Assuming FIVE_POINTS exists in CalibrationMode
        else:
            raise ValueError("Invalid calibration mode. Must be 2, 5, or a CalibrationMode instance.")