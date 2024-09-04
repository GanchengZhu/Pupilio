#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: GC Zhu
# Email: zhugc2016@gmail.com
import json
import logging
import math
import os
import platform
import random
import time
from datetime import datetime

import numpy as np
import pygame
from pygame import Rect

from .misc import ET_ReturnCode, LocalConfig, Calculator


class CalibrationUI(object):
    def __init__(self, pupil_io):

        # set deep gaze
        self._pupil_io = pupil_io

        # set pygame window caption
        # pygame.display.set_caption('deep gaze calibration')

        # set pygame window icon
        # _icon_path = os.path.join(self._current_dir, "asset", "pupil_io_favicon.png")
        # _icon = pygame.image.load(_icon_path)
        # pygame.display.set_icon(_icon)

        # constant fonts
        if platform.system().lower() == 'windows':
            if "microsoftyaheiui" in pygame.font.get_fonts():
                _font_name = "microsoftyaheiui"
            else:
                _font_name = pygame.font.get_fonts()[0]

            self._font = pygame.font.SysFont(_font_name, 36, bold=False, italic=False)
            self._error_text_font = pygame.font.SysFont(_font_name, 24, bold=False, italic=False)
            self._instruction_font = pygame.font.SysFont(_font_name, 24, bold=False, italic=False)

        elif platform.system().lower() == 'linux':
            self._font = pygame.font.Font(None, 36)
            self._error_text_font = pygame.font.Font(None, 18)
            self._instruction_font = pygame.font.Font(None, 24)

        # constant colors
        self._BLACK = (0, 0, 0)
        self._RED = (255, 0, 0)
        self._GREEN = (0, 255, 0)
        self._BLUE = (0, 0, 255)
        self._WHITE = (255, 255, 255)
        self._CRIMSON = (220, 20, 60)
        self._CORAL = (240, 128, 128)
        self._GRAY = (128, 128, 128)

        # constant calibration points
        self._calibrationPoint = [
            (576, 540), (1344, 540)
        ]

        # constant calibration stuffs
        self._target_size = 16
        self._inner_circle_size = 9
        self._face_in_rect = pygame.Rect(660, 240, 600, 600)

        # constant library path
        self._current_dir = os.path.abspath(os.path.dirname(__file__))

        # audio path
        self._beep_sound_path = os.path.join(self._current_dir, "asset", "beep.wav")
        self._calibration_instruction_sound_path = os.path.join(self._current_dir, "asset",
                                                                "calibration_instruction.wav")
        # 戴凯@2024/4/23
        self._adjust_position_sound_path = os.path.join(self._current_dir, "asset", "adjust_position.wav")

        # load audio files
        pygame.mixer.init()
        self._sound = pygame.mixer.Sound(self._beep_sound_path)
        self._cali_ins_sound = pygame.mixer.Sound(self._calibration_instruction_sound_path)
        # 戴凯@2024/4/23
        self._just_pos_sound = pygame.mixer.Sound(self._adjust_position_sound_path)

        self._just_pos_sound_once = False

        # image transformer
        _rotate = pygame.transform.rotate
        _scale = pygame.transform.scale

        # set mouse cursor invisible
        pygame.mouse.set_visible(False)

        # load face image
        self._frowning_face = pygame.image.load(os.path.join(self._current_dir, "asset", "frowning-face.png"))
        self._smiling_face = pygame.image.load(os.path.join(self._current_dir, "asset", "smiling-face.png"))

        # constant animation frequency (times per second)
        self._animation_frequency = 2

        # clock counter
        self._clock_resource_dict = {}
        self._clock_resource_height = 100
        for n in range(0, 10):
            self._clock_resource_dict[str(n)] = pygame.image.load(
                os.path.join(self._current_dir, "asset", f"figure_{n}.png"))
        self._clock_resource_dict['.'] = pygame.image.load(os.path.join(self._current_dir, "asset", "dot.png"))

        for key in self._clock_resource_dict:
            _img = self._clock_resource_dict[key]
            self._clock_resource_dict[key] = _scale(
                _img,
                (self._clock_resource_height / (_img.get_height() / _img.get_width()), self._clock_resource_height))

        # load local config
        self._local_config = LocalConfig()
        # self._screen = pygame.display.set_mode((self._screen_width, self._screen_height))
        self._screen = pygame.display.get_surface()
        self._screen.fill(self._BLACK)

        # get monitor size
        self._screen_width = self._local_config.dp_config['screen_width']
        self._screen_height = self._local_config.dp_config['screen_height']
        logging.info("screen size: %d x %d" % (self._screen_width, self._screen_height))

        self._calculator = Calculator(
            screen_width=self._screen_width,
            screen_height=self._screen_height,
            physical_screen_width=self._local_config.dp_config['physical_screen_width'],
            physical_screen_height=self._local_config.dp_config['physical_screen_height'])

        self._calibration_bounds = Rect(0, 0, self._screen_width, self._screen_height)

        # do a quick 5-point validation of the calibration results
        self._validation_points = [
            [0.5, 0.08],
            [0.08, 0.5], [0.92, 0.5],
            [0.5, 0.92]]
        random.shuffle(self._validation_points)
        self._validation_points += [[0.5, 0.5]]

        # scale
        for _point in self._validation_points:
            _point[0] = _point[0] * (
                    self._calibration_bounds.width - self._calibration_bounds.left) - self._target_size / 2
            _point[1] = _point[1] * (
                    self._calibration_bounds.height - self._calibration_bounds.top) - self._target_size / 2

        # image resource for calibration and validation points
        _source_image = pygame.image.load(os.path.join(self._current_dir, "asset", "windmill.png"))
        _max_size, _min_size = 60, 20
        self._animation_size = [
            (_min_size + (_max_size - _min_size) * i / 19, _min_size + (_max_size - _min_size) * i / 19)
            for i in range(20)
        ]
        self._animation_list = [
            _rotate(_scale(_source_image, self._animation_size[i]), 40 * i * 0)
            for i in range(10)
        ]

        """
        variable
        """
        self._phase_adjust_position = True
        self._calibration_preparing = False
        self._validation_preparing = False
        self._phase_calibration = False
        self._phase_validation = False
        self._need_validation = False
        self.graphics_finished = False
        self._exit = False
        self._calibration_drawing_list = [0, 1, 2, 3, 4]
        self._calibration_timer = 0
        self._validation_timer = 0
        self._validation_left_sample_store = [[] * len(self._validation_points)]
        self._validation_right_sample_store = [[] * len(self._validation_points)]
        self._validation_left_eye_distance_store = [[] * len(self._validation_points)]
        self._validation_right_eye_distance_store = [[] * len(self._validation_points)]
        self._n_validation = 0  # n times of validation
        self._error_threshold = 2
        self._calibration_point_index = 0
        self._drawing_validation_result = False
        self._hands_free = False
        # daikai@20240423
        self._hands_free_adjust_head_wait_time = 12  # 3
        self._hands_free_adjust_head_start_timestamp = 0
        self._validation_finished_timer = 0

    def initialize_variables(self):
        """Initialize variables for plotting and visualization."""
        self._phase_adjust_position = True
        self._calibration_preparing = False
        self._validation_preparing = False
        self._phase_calibration = False
        self._phase_validation = False
        self._need_validation = False
        self.graphics_finished = False
        self._exit = False
        self._calibration_drawing_list = [0, 1, 2, 3, 4]
        self._calibration_timer = 0
        self._validation_timer = 0
        self._validation_left_sample_store = [[] for _ in range(len(self._validation_points) + 1)]
        self._validation_right_sample_store = [[] for _ in range(len(self._validation_points) + 1)]
        self._validation_left_eye_distance_store = [[] for _ in range(len(self._validation_points) + 1)]
        self._validation_right_eye_distance_store = [[] for _ in range(len(self._validation_points) + 1)]
        self._n_validation = 0  # n times of validation
        self._error_threshold = 2
        self._calibration_point_index = 0
        self._drawing_validation_result = False
        self._hands_free = False
        self._hands_free_adjust_head_wait_time = 12  # 3
        self._hands_free_adjust_head_start_timestamp = 0
        self._validation_finished_timer = 0

    def _draw_error_line(self, ground_truth_point, estimated_point, error_color):
        fixation_text = "+"
        text_surface = self._font.render(fixation_text, True, self._GREEN)
        text_rect = text_surface.get_rect()
        text_rect.center = (ground_truth_point[0],
                            ground_truth_point[1])
        self._screen.blit(text_surface, text_rect)

        fixation_text = "+"
        text_surface = self._font.render(fixation_text, True, error_color)
        text_rect = text_surface.get_rect()

        if not isinstance(estimated_point, np.ndarray):
            return
        text_rect.center = (estimated_point[0],
                            estimated_point[1])
        self._screen.blit(text_surface, text_rect)

        pygame.draw.line(self._screen, self._BLACK, ground_truth_point, estimated_point, width=1)

    def _draw_error_text(self, min_error, ground_truth_point, is_left=True):
        # error_degrees = self._calculator.error(ground_truth_point, estimated_point,
        #                                        eye_distance)
        error_degrees = min_error
        height_position = 1
        # 将错误以两位小数显示，并加上度符号
        if is_left:
            error_text = f"L: {error_degrees:.2f}°"
        else:
            error_text = f"R: {error_degrees:.2f}°"
            height_position += 1
        # 渲染文本
        text_surface = self._error_text_font.render(error_text, True, self._BLACK)
        text_rect = text_surface.get_rect()

        # 将文本居中
        text_rect.center = (ground_truth_point[0],
                            ground_truth_point[1] + text_rect.height * height_position)

        # 将文本绘制到屏幕上
        self._screen.blit(text_surface, text_rect)

    def _draw_legend(self):
        legend_texts = ["Target coordinates", "Left eye gaze coordinates", "Right eye gaze coordinates"]
        color_list = [self._GREEN, self._CRIMSON, self._CORAL]
        x = 128
        y = self._screen_height - 128

        for n, content in enumerate(legend_texts):
            add_text_surface = self._error_text_font.render("+", True, color_list[n])
            add_text_rect = add_text_surface.get_rect()
            add_text_rect.center = (x, y)
            # text_rect.center = (self._screen_width // 2 + n * text_rect.width, self._screen_height // 2)
            self._screen.blit(add_text_surface, add_text_rect)
            _x = x + add_text_rect.width

            content_text_surface = self._error_text_font.render(content, True, self._BLACK)
            content_text_rect = content_text_surface.get_rect()
            _x += content_text_rect.width // 2
            content_text_rect.center = (_x, y)
            # text_rect.center = (self._screen_width // 2 + n * text_rect.width, self._screen_height // 2)
            self._screen.blit(content_text_surface, content_text_rect)
            y += content_text_rect.height + 3

    def _recalibration(self):
        for idx in range(len(self._validation_points)):
            _left_samples = self._validation_left_sample_store[idx]  # n * 2
            _right_samples = self._validation_right_sample_store[idx]  # n * 2
            if len(_left_samples) <= 5 or len(_right_samples) <= 5:  # 小于五个样本点，说明该点需要重新校准
                # less than ten samples collected
                self._validation_left_sample_store[idx] = []
                self._validation_left_eye_distance_store[idx] = []
                self._validation_right_sample_store[idx] = []
                self._validation_right_eye_distance_store[idx] = []
                self._calibration_drawing_list.append(idx)
            else:
                _left_samples = self._validation_left_sample_store[idx]  # n * 2
                _right_samples = self._validation_right_sample_store[idx]  # n * 2
                _left_eye_distances = self._validation_left_eye_distance_store[idx]  # n * 1
                _right_eye_distances = self._validation_right_eye_distance_store[idx]  # n * 1
                _ground_truth_point = self._validation_points[idx]

                _left_res = self._calculator.calculate_error_by_sliding_window(
                    gt_point=_ground_truth_point, es_points=_left_samples,
                    distances=_left_eye_distances
                )
                _right_res = self._calculator.calculate_error_by_sliding_window(
                    gt_point=_ground_truth_point, es_points=_right_samples,
                    distances=_right_eye_distances
                )

                if (_left_res["min_error"] > self._error_threshold
                        or _right_res["min_error"] > self._error_threshold):
                    logging.info(f"Recalibration point index: {idx}, Left error: {_left_res['min_error']}, "
                                 f"Right error: {_right_res['min_error']}")
                    # 如果误差大于设定值该点的所有数据清空，并且重新加入校准
                    self._validation_left_eye_distance_store[idx] = []
                    self._validation_left_sample_store[idx] = []
                    self._validation_right_eye_distance_store[idx] = []
                    self._validation_right_sample_store[idx] = []
                    self._calibration_drawing_list.append(idx)

        if not self._calibration_drawing_list:  # 不需要再次校准了
            self._n_validation = 2

    def _draw_validation_point(self):
        # 校准点不存在了，也就是校准结束
        if not self._calibration_drawing_list:
            # whether to revalidation
            if self._n_validation == 1:  # 是否进行重新校准
                self._recalibration()
            else:
                if self._hands_free and not self._validation_finished_timer:
                    self._validation_finished_timer = time.time()
                elif self._hands_free and self._validation_finished_timer:
                    __time_elapsed = time.time() - self._validation_finished_timer
                    if __time_elapsed > 3:
                        self._phase_validation = False

                _calibrationDir = (self._pupil_io._workSpace.joinpath("calibration")
                                   .joinpath(self._pupil_io._session_name))
                if not _calibrationDir.exists():
                    _calibrationDir.mkdir(parents=True)

                _currentTime = datetime.now()
                _timeString = _currentTime.strftime("%Y-%m-%d_%H-%M-%S")

                with _calibrationDir.joinpath(f"{_timeString}.json").open('w') as handle:
                    json.dump({
                        "validation_left_samples": self._validation_left_sample_store,
                        "validation_right_samples": self._validation_right_sample_store,
                        "validation_ground_truth_point": self._validation_points,
                        "validation_left_eye_distances": self._validation_left_eye_distance_store,
                        "validation_right_eye_distances": self._validation_right_eye_distance_store
                    }, handle)

                for idx in range(len(self._validation_points)):
                    _left_samples = self._validation_left_sample_store[idx]  # n * 2
                    _right_samples = self._validation_right_sample_store[idx]  # n * 2
                    _left_eye_distances = self._validation_left_eye_distance_store[idx]  # n * 1
                    _right_eye_distances = self._validation_right_eye_distance_store[idx]  # n * 1
                    _ground_truth_point = self._validation_points[idx]



                    if _left_samples:
                        # modified it by slide window
                        # _avg_left_eye_distance = np.mean(_left_eye_distances)
                        # _avg_left_eye_sample = np.mean(_left_samples, axis=0)

                        _res = self._calculator.calculate_error_by_sliding_window(
                            gt_point=_ground_truth_point, es_points=_left_samples,
                            distances=_left_eye_distances
                        )

                        if _res:
                            self._draw_error_line(_ground_truth_point, _res["min_error_es_point"], self._CRIMSON)
                            self._draw_error_text(_res["min_error"], _ground_truth_point,
                                                  is_left=True)

                    if _right_samples:
                        _res = self._calculator.calculate_error_by_sliding_window(
                            gt_point=_ground_truth_point, es_points=_right_samples,
                            distances=_right_eye_distances
                        )

                        if _res:
                            self._draw_error_line(_ground_truth_point, _res["min_error_es_point"], self._CRIMSON)
                            self._draw_error_text(_res["min_error"], _ground_truth_point,
                                                  is_left=False)

                    self._draw_legend()
                    self._drawing_validation_result = True

        else:
            # initial for each point
            if self._validation_timer == 0:
                self._sound.play()
                self._validation_timer = time.time()

            _time_elapsed = time.time() - self._validation_timer
            if _time_elapsed > 1.5:
                self._calibration_drawing_list.pop()
                self._validation_timer = 0
                if not self._calibration_drawing_list:
                    self._n_validation += 1  # 检查是否重新进行校准
                else:
                    logging.info("Validation point index: " + str(self._calibration_drawing_list[-1]))

            else:
                _point = self._validation_points[self._calibration_drawing_list[-1]]
                _status, _left_sample, _right_sample, _timestamp, _marker = self._pupil_io.estimation_lr()

                self._draw_animation(point=_point, time_elapsed=_time_elapsed)

                if 0.0 < _time_elapsed <= 1.5:
                    # face_status, face_position = self._pupil_io.face_position()
                    _left_sample = _left_sample.tolist()
                    _right_sample = _right_sample.tolist()
                    _left_gaze_point = [_left_sample[0], _left_sample[1]]
                    _right_gaze_point = [_right_sample[0], _right_sample[1]]
                    # _eyebrow_distance = math.fabs(face_position[2]) / 10
                    # logging.info("validation left gaze estimated example: " + str(_left_sample))
                    # logging.info("validation right gaze estimated example: " + str(_right_sample))
                    if _left_sample[13] == 1:
                        self._validation_left_sample_store[self._calibration_drawing_list[-1]].append(
                            _left_gaze_point
                        )
                        self._validation_left_eye_distance_store[self._calibration_drawing_list[-1]].append(
                            math.fabs(_left_sample[5]) / 10
                        )
                    else:
                        logging.info(
                            f"calibration left eye sample loss, "
                            f"calibration position index: {self._calibration_drawing_list[-1]},"
                            f"calibration position: {self._validation_points[self._calibration_drawing_list[-1]]}")
                    if _right_sample[13] == 1:
                        self._validation_right_sample_store[self._calibration_drawing_list[-1]].append(
                            _right_gaze_point
                        )
                        self._validation_right_eye_distance_store[self._calibration_drawing_list[-1]].append(
                            math.fabs(_right_sample[5]) / 10
                        )
                    else:
                        logging.info(
                            f"calibration sample right eye loss, "
                            f"calibration position index: {self._calibration_drawing_list[-1]},"
                            f"calibration position: {self._validation_points[self._calibration_drawing_list[-1]]}")

    def _draw_calibration_point(self):
        if self._calibration_timer == 0:
            self._sound.play()
            self._calibration_timer = time.time()

        _time_elapsed = time.time() - self._calibration_timer

        _status = self._pupil_io.calibration(self._calibration_point_index)
        if _status == ET_ReturnCode.ET_CALI_CONTINUE.value:
            pass
        elif _status == ET_ReturnCode.ET_CALI_NEXT_POINT.value:
            self._calibration_point_index += 1
            self._calibration_timer = 0
            self._sound.play()
        elif _status == ET_ReturnCode.ET_SUCCESS.value:
            self._phase_calibration = False
            self._validation_preparing = False
            if self._need_validation and not self._hands_free:
                self._validation_preparing = True
                self._phase_validation = False
            elif self._hands_free and self._need_validation:
                self._phase_calibration = False
                self._validation_preparing = False
                self._phase_validation = True
            else:
                self._exit = True
                self.graphics_finished = True

        _point = self._calibrationPoint[self._calibration_point_index]
        self._draw_animation(point=_point, time_elapsed=_time_elapsed)

    def _draw_animation(self, point, time_elapsed):
        _index = int(time_elapsed // (1 / (self._animation_frequency * 10))) % 10
        _width = self._animation_size[_index][0]
        _height = self._animation_size[_index][1]
        self._screen.blit(self._animation_list[_index], (
            point[0] - _width // 2, point[1] - _height // 2
        ))

    def _draw_adjust_position(self):
        if (not self._just_pos_sound_once):
            self._just_pos_sound.play()
            self._just_pos_sound_once = True
            # time.sleep(5)

        _instruction_text = " "
        _color = [255, 255, 255]
        _eyebrow_center_point = [-1, -1]
        _start_time = time.time()
        _status, _face_position = self._pupil_io.face_position()
        _face_position = _face_position.tolist()
        logging.info(f'Get face position cost {(time.time() - _start_time):.4f} seconds.')
        logging.info(f'Face position: {str(_face_position)}')

        _face_pos_x = _face_position[0]
        _face_pos_y = _face_position[1]
        _face_pos_z = _face_position[2]  # Emulating face_pos.z for testing

        # face cartoon

        # Update face point
        _eyebrow_center_point[0] = 960 + (_face_pos_x - 172.08) * 10
        _eyebrow_center_point[1] = 540 + (_face_pos_y - 96.79) * 10

        # Update rectangle color based on face point inside the rectangle
        if self._face_in_rect.collidepoint(_eyebrow_center_point):
            _rectangle_color = self._GREEN
        else:
            _rectangle_color = self._RED
            _instruction_text = "请把头移动到方框中央"

        # Update face point color based on face position in Z-axis
        if _face_pos_z == 0:
            _face_pos_z = 65536
        _color_ratio = 280 / abs(_face_pos_z)
        if _face_pos_z > -530 or _face_pos_z < -630:
            _face = self._frowning_face
            _face_point_color = self._RED
            if _face_pos_z > -530:
                _instruction_text = "远一点"
            if _face_pos_z < -630:
                _instruction_text = "近一点"
        else:
            _face = self._smiling_face
            _face_point_color = tuple(
                np.multiply(self._GREEN, (1 - _color_ratio)) + np.multiply(self._RED, _color_ratio))

        # scale the face image
        _face = pygame.transform.scale(_face, (int(_color_ratio * 256), int(_color_ratio * 256)))
        _face_w, _face_h = _face.get_size()

        # Draw rectangle
        pygame.draw.rect(self._screen, _rectangle_color, (610, 190, 700, 700), 10)

        if _status == ET_ReturnCode.ET_SUCCESS.value or not (
                _face_position[0] == 0 and _face_position[1] == 0 and _face_position[2] == 0):
            # Draw face point as a circle
            # pygame.draw.circle(self._screen, _face_point_color, (int(_eyebrow_center_point[0]),
            #                                                      int(_eyebrow_center_point[1])), 50)
            self._screen.blit(_face, (int(_eyebrow_center_point[0]), int(_eyebrow_center_point[1])))

        # _instruction_text = " "
        # _instruction_text = "  \n请调整人脸至合适的姿势以及合适的距离\n待小球与框框变绿\n按Enter键进行下一步"

        _segment_text = _instruction_text.split("\n")
        _shift = 0
        for t in _segment_text:
            text_surface = self._font.render(t, True, self._BLACK)
            text_rect = text_surface.get_rect()
            # text_rect.center = (self._screen_width // 2,
            #                     190 + 700 + 20 + _shift)
            text_rect.center = (int(_eyebrow_center_point[0] + _face_w // 2),
                                int(_eyebrow_center_point[1]) + 100 + _shift + _face_h // 2)
            _shift += text_rect.height
            self._screen.blit(text_surface, text_rect)

        if self._hands_free:
            if (-630 <= _face_pos_z <= -530 and self._face_in_rect.collidepoint(_eyebrow_center_point)
                    and self._hands_free_adjust_head_wait_time <= 0):
                # meet the criterion and wait time > 0
                self._phase_adjust_position = False
                self._calibration_preparing = True
            elif (-630 <= _face_pos_z <= -530 and self._face_in_rect.collidepoint(_eyebrow_center_point)
                  and not self._hands_free_adjust_head_wait_time <= 0):
                if self._hands_free_adjust_head_start_timestamp == 0:
                    self._hands_free_adjust_head_start_timestamp = time.time()
                else:
                    _tmp = time.time()
                    self._hands_free_adjust_head_wait_time -= (_tmp - self._hands_free_adjust_head_start_timestamp)
                    self._hands_free_adjust_head_start_timestamp = _tmp
            else:
                self._hands_free_adjust_head_start_timestamp = 0

    def _draw_text_center(self, text):
        self._draw_segment_text(text, self._screen_width // 2, self._screen_height // 2)

    def _draw_segment_text(self, text, x, y):
        _segment_text = text.split("\n")
        _shift = 0
        for t in _segment_text:
            text_surface = self._font.render(t, True, self._BLACK)
            text_rect = text_surface.get_rect()
            text_rect.center = (x, y + _shift)
            _shift += text_rect.height
            self._screen.blit(text_surface, text_rect)

    def _draw_calibration_preparing(self):
        _text = "接下来会出现两个点，请依次注视它们\n按回车键进入校准"
        self._draw_text_center(_text)

    def _draw_calibration_preparing_hands_free(self):
        if not self._preparing_hands_free_start:
            self._preparing_hands_free_start = time.time()
            self._cali_ins_sound.play()

        _time_elapsed = time.time() - self._preparing_hands_free_start
        if _time_elapsed <= 9.0:
            # daikai@2024.04.23
            _text = "倒计时结束后，屏幕上会出现几个点，请依次注视它们。"  # "9秒钟后，屏幕上会出现几个点，请依次注视它们"
            _center_x = self._screen_width // 2
            _center_y = self._screen_height // 2
            self._draw_segment_text(_text, _center_x, _center_y)
            _rest = "%d" % (10 - _time_elapsed)
            _w = self._clock_resource_dict['.'].get_width()
            _h = self._clock_resource_dict['.'].get_height()

            for n, _character in enumerate(_rest):
                # _x = _center_x - (3 - n) * _w
                _x = _center_x - _w
                _y = _center_y - 200
                self._screen.blit(self._clock_resource_dict[_character], (_x + _w // 2, _y + _h // 2))
        else:
            self._calibration_preparing = False
            self._phase_calibration = True

    def _draw_validation_preparing(self):
        _text = "接下来会出现五个点，请注视它们\n按回车键进入验证"
        self._draw_text_center(_text)

    def draw(self, validate=False, bg_color=(255, 255, 255)):
        self.initialize_variables()
        self._need_validation = validate
        while not self._exit:
            for event in pygame.event.get():
                # if event.type == pygame.quit():
                #     break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self._phase_adjust_position:
                        self._phase_adjust_position = False
                        self._calibration_preparing = True

                    elif event.key == pygame.K_RETURN and self._calibration_preparing:
                        self._phase_adjust_position = False
                        self._calibration_preparing = False
                        self._phase_calibration = True

                    elif event.key == pygame.K_RETURN and self._validation_preparing:
                        self._phase_validation = True
                        self._validation_preparing = False

                    elif event.key == pygame.K_RETURN and self._phase_validation and self._drawing_validation_result:
                        self._phase_validation = False

                    elif event.key == pygame.K_q:
                        self._exit = True

            # self._fps_clock.tick(self._fps)
            # draw white background
            self._screen.fill(bg_color)  # Fill white color
            # draw point
            if not self._phase_adjust_position and not self._calibration_preparing and self._phase_calibration:
                self._draw_calibration_point()
            elif self._calibration_preparing:
                # pygame.draw.circle(self._screen, self._RED, (0, 0), self._target_size, self._inner_circle_size)
                self._draw_calibration_preparing()
            elif self._validation_preparing:
                self._draw_validation_preparing()

            elif self._phase_adjust_position:
                self._draw_adjust_position()
            elif self._phase_validation:
                self._draw_validation_point()

            elif (not self._phase_validation and not self._calibration_preparing and
                  not self._phase_calibration and not self._phase_adjust_position
                  and not self._validation_preparing):
                self.graphics_finished = True
                break

            pygame.display.flip()
        self._sound.stop()
        # pygame.quit()

    def draw_hands_free(self, validate=False, bg_color=(255, 255, 255)):
        self.initialize_variables()
        self._need_validation = validate
        self._preparing_hands_free_start = 0
        self._hands_free = True
        while not self._exit:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self._exit = True

            self._screen.fill(bg_color)  # Fill bg color
            # draw point
            if self._phase_calibration:
                self._draw_calibration_point()
            elif self._calibration_preparing:
                # pygame.draw.circle(self._screen, self._RED, (0, 0), self._target_size, self._inner_circle_size)
                self._draw_calibration_preparing_hands_free()
            # elif self._validation_preparing:
            #     self._draw_validation_preparing_hands_free()
            elif self._phase_adjust_position:
                self._draw_adjust_position()
            elif self._phase_validation:
                self._draw_validation_point()

            elif (not self._phase_validation and not self._calibration_preparing and
                  not self._phase_calibration and not self._phase_adjust_position
                  and not self._validation_preparing):
                self.graphics_finished = True
                break

            pygame.display.flip()
        self._sound.stop()


