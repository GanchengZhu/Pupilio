# _*_ coding: utf-8 _*_
# Copyright (c) 2024, Hangzhou Deep Gaze Sci & Tech Ltd
# All Rights Reserved
#
# For use by  Hangzhou Deep Gaze Sci & Tech Ltd licencees only.
# Redistribution and use in source and binary forms, with or without
# modification, are NOT permitted.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in
# the documentation and/or other materials provided with the distribution.
#
# Neither name of  Hangzhou Deep Gaze Sci & Tech Ltd nor the name of
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS
# IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# DESCRIPTION:
# This demo shows how to configure the calibration process

# Author: GC Zhu
# Email: zhugc2016@gmail.com

import os
from pathlib import Path

from .misc import CalibrationMode


class DefaultConfig:
    """
    Default configuration class containing various parameters required for program execution.
    Includes settings for file paths, hyperparameters, and resources like images and audio.

    Attributes:
        - Current Directory:
            Stores the absolute path of the current file's directory for constructing resource file paths.

        - Filter Hyperparameters:
            `look_ahead` (int): Look-ahead steps for predicting target position.

        - Calibration Resources:
            `cali_target_beep` (str): Path to the beep sound used during calibration.
            `cali_frowning_face_img` (str): Path to the frowning face image used during calibration.
            `cali_smiling_face_img` (str): Path to the smiling face image used during calibration.
            `cali_target_img` (str): Path to the windmill image used as the calibration target.

        - Calibration Target Settings:
            `cali_target_img_maximum_size` (int): Maximum size of the calibration target image.
            `cali_target_img_minimum_size` (int): Minimum size of the calibration target image.
            `cali_target_animation_frequency` (int): Frequency of the calibration target animation (in Hz).

        - Calibration Mode:
            `cali_mode` (CalibrationMode): Specifies the calibration mode, default is TWO_POINTS.

        - Kappa Angle Verification:
            `enable_kappa_verification` (int): Verification of the kappa angle after calibration. Default is 1.
                                         When this value is 0, the verification of the kappa angle after calibration
                                         is disabled, suitable for users with strabismus.

        Debug Settings:
            - `enable_debug_logging` (int): Toggle for enabling debug logging. Disabled by default (0).
            - `log_directory` (str): Directory path for storing debug logs.

        Calibration Instructions:
            - `instruction_face_far` (str): Instruction when the face is too close.
            - `instruction_face_near` (str): Instruction when the face is too far.
            - `instruction_head_center` (str): Instruction to align the head to the center of the frame.
            - `instruction_enter_calibration` (str): Instruction for entering calibration.
            - `instruction_hands_free_calibration` (str): Instruction for hands-free calibration.

        Validation Instructions:
            - `instruction_enter_validation` (str): Instruction for entering validation.

        Validation Legends:
            - `legend_target` (str): Legend for target points.
            - `legend_left_eye` (str): Legend for left eye gaze.
            - `legend_right_eye` (str): Legend for right eye gaze.
            - `instruction_calibration_over` (str): Instruction for continuing after validation.
            - `instruction_recalibration` (str): Instruction for initiating recalibration.
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

        # Verification of the kappa angle after calibration, default is 1.
        # When this value is 0, the verification of the kappa angle after calibration
        # is disabled, suitable for users with strabismus.
        self.enable_kappa_verification = 1

        # debug parameters
        self.enable_debug_logging = 0
        self.log_directory = str(Path.home().absolute() / "Pupilio" / "native_log")

        # for calibration previewer
        # Calibration preview instructions
        self.instruction_face_far = "Move further away"  # Instruction when the face is too close (instruction_face_far)
        self.instruction_face_near = "Move closer"  # Instruction when the face is too far (instruction_face_near)
        self.instruction_head_center = "Please move your head to the center of the frame"  # Instruction to align head to the center (instruction_head_center)

        # Calibration entry instructions
        self.instruction_enter_calibration = (
            "Two points will appear. Please look at them in sequence.\n"
            "Press Enter or click on the screen (left mouse button) to start calibration."
        )  # Instruction for entering calibration (instruction_enter_calibration)
        self.instruction_hands_free_calibration = (
            "After the countdown, several points will appear. Please look at them in sequence."
        )  # Instruction for hands-free calibration (instruction_hands_free_calibration)

        # Validation entry instructions
        self.instruction_enter_validation = (
            "Five points will appear. Please look at them.\n"
            "Press Enter or click on the screen (left mouse button) to start validation."
        )  # Instruction for entering validation (instruction_enter_validation)

        # Validation result legends
        self.legend_target = "Target"  # Legend label for target points (legend_target)
        self.legend_left_eye = "Left Eye Gaze"  # Legend label for left eye gaze (legend_left_eye)
        self.legend_right_eye = "Right Eye Gaze"  # Legend label for right eye gaze (legend_right_eye)
        self.instruction_calibration_over = (
            "Press \"Enter\" or click on the screen to continue."
        )  # Instruction for continuing after validation (legend_continue)
        self.instruction_recalibration = (
            "Press \"R\" or double click on the screen to recalibrate."
        )  # Instruction for initiating recalibration (legend_recalibration)

        self.instruction_language()

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

    def instruction_language(self, lang='simplified_chinese'):
        """
        Update the instructions and legends based on the specified language.

        Parameters:
            lang (str): The language to update to. Supported values are:
                - 'simple_chinese': Updates instructions to Simplified Chinese.
                - 'traditional_chinese': Updates instructions to Traditional Chinese.
                - 'english': Updates instructions to English.
                - 'french': Updates instructions to French.
                - 'spanish': Updates instructions to Spanish.

        Raises:
            ValueError: If an unsupported language is specified.
        """

        if lang == 'simplified_chinese':
            self.simplified_chinese()
        elif lang == 'traditional_chinese':
            self.traditional_chinese()
        elif lang == 'english':
            self.english()
        elif lang == 'french':
            self.french()
        elif lang == 'spanish':
            self.spanish()
        else:
            raise ValueError(f"Unsupported language: {lang}")

    def simplified_chinese(self):
        """
        Update all instructions and legends to Simplified Chinese.
        """
        # Calibration preview instructions
        self.instruction_face_far = "请往后移远些"
        self.instruction_face_near = "请靠近一些"
        self.instruction_head_center = "请将头移动到画面中央"

        # Calibration entry instructions
        self.instruction_enter_calibration = (
            "屏幕上会出现两个点，请按顺序注视这些点。\n"
            "按下回车键或点击屏幕（或者鼠标左键）开始校准。"
        )
        self.instruction_hands_free_calibration = (
            "倒计时后屏幕会显示几个点，请按顺序注视这些点。"
        )

        # Validation entry instructions
        self.instruction_enter_validation = (
            "屏幕上会出现五个点，请注视这些点。\n"
            "按下回车键或点击屏幕（或者鼠标左键）开始验证。"
        )

        # Validation result legends
        self.legend_target = "目标点"
        self.legend_left_eye = "左眼注视点"
        self.legend_right_eye = "右眼注视点"
        self.instruction_calibration_over = (
            "按下\"回车键\"或点击屏幕（或者鼠标左键）继续。"
        )
        self.instruction_recalibration = (
            "按下\"R\"键或双击屏幕（或者双击鼠标左键）重新校准。"
        )

    def traditional_chinese(self):
        """
        Update all instructions and legends to Traditional Chinese.
        """
        # Calibration preview instructions
        self.instruction_face_far = "請往後退一點"
        self.instruction_face_near = "請靠近一點"
        self.instruction_head_center = "請將頭部置於畫面中央"

        # Calibration entry instructions
        self.instruction_enter_calibration = (
            "螢幕上將出現兩個點，請依次注視。\n"
            "按下 Enter 鍵或點擊螢幕（或滑鼠左鍵）開始校準。"
        )
        self.instruction_hands_free_calibration = (
            "倒數計時後，螢幕上將出現多個點，請依次注視。"
        )

        # Validation entry instructions
        self.instruction_enter_validation = (
            "螢幕上將出現五個點，請注視這些點。\n"
            "按下 Enter 鍵或點擊螢幕（或滑鼠左鍵）開始驗證。"
        )

        # Validation result legends
        self.legend_target = "目標點"
        self.legend_left_eye = "左眼注視點"
        self.legend_right_eye = "右眼注視點"
        self.instruction_calibration_over = (
            "按下 \"Enter\" 或點擊螢幕（或滑鼠左鍵）繼續。"
        )
        self.instruction_recalibration = (
            "按下 \"R\" 或雙擊螢幕（或滑鼠左鍵雙擊）重新校準。"
        )

    def english(self):
        """
        Update all instructions and legends to English.
        """
        # Calibration preview instructions
        self.instruction_face_far = "Please move further back"
        self.instruction_face_near = "Please move closer"
        self.instruction_head_center = "Please center your head in the frame"

        # Calibration entry instructions
        self.instruction_enter_calibration = (
            "Two points will appear on the screen. Please look at them in sequence.\n"
            "Press the Enter key or click on the screen (or left mouse button) to start calibration."
        )
        self.instruction_hands_free_calibration = (
            "After the countdown, several points will appear on the screen. Please look at them in sequence."
        )

        # Validation entry instructions
        self.instruction_enter_validation = (
            "Five points will appear on the screen. Please look at them.\n"
            "Press the Enter key or click on the screen (or left mouse button) to start validation."
        )

        # Validation result legends
        self.legend_target = "Target Point"
        self.legend_left_eye = "Left Eye Gaze Point"
        self.legend_right_eye = "Right Eye Gaze Point"
        self.instruction_calibration_over = (
            "Press \"Enter\" or click on the screen (or left mouse button) to continue."
        )
        self.instruction_recalibration = (
            "Press \"R\" or double-click on the screen (or double left-click) to recalibrate."
        )

    def french(self):
        """
        Update all instructions and legends to French.
        """
        # Calibration preview instructions
        self.instruction_face_far = "Veuillez vous éloigner un peu"
        self.instruction_face_near = "Veuillez vous rapprocher"
        self.instruction_head_center = "Veuillez centrer votre tête dans le cadre"

        # Calibration entry instructions
        self.instruction_enter_calibration = (
            "Deux points apparaîtront à l'écran. Veuillez les regarder dans l'ordre.\n"
            "Appuyez sur la touche Entrée ou cliquez sur l'écran (ou bouton gauche de la souris) pour commencer la calibration."
        )
        self.instruction_hands_free_calibration = (
            "Après le compte à rebours, plusieurs points apparaîtront à l'écran. Veuillez les regarder dans l'ordre."
        )

        # Validation entry instructions
        self.instruction_enter_validation = (
            "Cinq points apparaîtront à l'écran. Veuillez les regarder.\n"
            "Appuyez sur la touche Entrée ou cliquez sur l'écran (ou bouton gauche de la souris) pour commencer la validation."
        )

        # Validation result legends
        self.legend_target = "Point Cible"
        self.legend_left_eye = "Point de Regard de l'Œil Gauche"
        self.legend_right_eye = "Point de Regard de l'Œil Droit"
        self.instruction_calibration_over = (
            "Appuyez sur \"Entrée\" ou cliquez sur l'écran (ou bouton gauche de la souris) pour continuer."
        )
        self.instruction_recalibration = (
            "Appuyez sur \"R\" ou double-cliquez sur l'écran (ou double-clic gauche) pour recalibrer."
        )

    def spanish(self):
        """
        Update all instructions and legends to Spanish.
        """
        # Calibration preview instructions
        self.instruction_face_far = "Por favor, aléjate un poco"
        self.instruction_face_near = "Por favor, acércate un poco"
        self.instruction_head_center = "Por favor, centra tu cabeza en el marco"

        # Calibration entry instructions
        self.instruction_enter_calibration = (
            "Aparecerán dos puntos en la pantalla. Por favor, míralos en secuencia.\n"
            "Presiona la tecla Enter o haz clic en la pantalla (o botón izquierdo del ratón) para comenzar la calibración."
        )
        self.instruction_hands_free_calibration = (
            "Después de la cuenta regresiva, aparecerán varios puntos en la pantalla. Por favor, míralos en secuencia."
        )

        # Validation entry instructions
        self.instruction_enter_validation = (
            "Aparecerán cinco puntos en la pantalla. Por favor, míralos.\n"
            "Presiona la tecla Enter o haz clic en la pantalla (o botón izquierdo del ratón) para comenzar la validación."
        )

        # Validation result legends
        self.legend_target = "Punto Objetivo"
        self.legend_left_eye = "Punto de Mirada del Ojo Izquierdo"
        self.legend_right_eye = "Punto de Mirada del Ojo Derecho"
        self.instruction_calibration_over = (
            "Presiona \"Enter\" o haz clic en la pantalla (o botón izquierdo del ratón) para continuar."
        )
        self.instruction_recalibration = (
            "Presiona \"R\" o haz doble clic en la pantalla (o doble clic izquierdo) para recalibrar."
        )
