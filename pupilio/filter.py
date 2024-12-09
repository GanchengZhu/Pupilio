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

import ctypes
import os
import platform

import numpy as np


class Filter:
    def __init__(self, look_ahead=2):
        """
        Filter class for processing gaze data using a native C/C++ library.

        :param look_ahead: Number of samples to look ahead for filtering (default is 20)
        """
        # Determine the platform and load the appropriate DLL
        if platform.system().lower() == 'windows':
            _current_dir = os.path.abspath(os.path.dirname(__file__))
            _lib_dir = os.path.join(_current_dir, "lib")
            os.add_dll_directory(_lib_dir)
            os.environ['PATH'] = _lib_dir + ';' + os.environ['PATH']
            # Load the DLL for Windows
            _dll_path = os.path.join(_lib_dir, 'libfilter.dll')
            self.filter_native_lib = ctypes.CDLL(_dll_path, winmode=0)
            self.filter_native_lib.init(look_ahead)

        else:
            _current_dir = os.path.abspath(os.path.dirname(__file__))
            _lib_dir = os.path.join(_current_dir, "lib")
            os.add_dll_directory(_lib_dir)
            os.environ['PATH'] = _lib_dir + ';' + os.environ['PATH']
            # Load the shared object library for Linux (Not currently supported)
            _dll_path = os.path.join(_lib_dir, 'libfilter.so')
            self.et_native_lib = ctypes.CDLL(_dll_path)
            # NOT SUPPORT LINUX NOW
            pass

        # Define the argument types for the filter functions
        self.filter_native_lib.do_filter_left.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS')]

        self.filter_native_lib.do_filter_right.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS')]

        self.filter_native_lib.do_filter_bino.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS')]

        # Initialize input and output arrays for left and right gaze
        self._left_input = np.zeros(2, dtype=np.float32)
        self._left_output = np.zeros(2, dtype=np.float32)

        self._right_input = np.zeros(2, dtype=np.float32)
        self._right_output = np.zeros(2, dtype=np.float32)

        self._bino_input = np.zeros(2, dtype=np.float32)
        self._bino_output = np.zeros(2, dtype=np.float32)

    def filter_sample(self, sample):
        """
        Filter a sample of left, right, and bino gaze.
        """

        _timestamp = sample['timestamp']

        # Extract samples
        _left_sample = sample['left_eye_sample']
        _right_sample = sample['right_eye_sample']
        _bino_sample = sample['bino_gaze_position']

        # Process left eye sample
        if _left_sample[0] is not np.nan and _left_sample[1] is not np.nan and _left_sample[13]:
            self._left_input = np.array([_left_sample[0], _left_sample[1]], dtype=np.float32)  # Convert to ndarray
            _flag_left = self.filter_native_lib.do_filter_left(self._left_input, self._left_output)
            sample['left_eye_sample'][:2] = self._left_output[:2]

        # Process right eye sample
        if _right_sample[0] is not np.nan and _right_sample[1] is not np.nan and _right_sample[13]:
            self._right_input = np.array([_right_sample[0], _right_sample[1]], dtype=np.float32)  # Convert to ndarray
            _flag_right = self.filter_native_lib.do_filter_right(self._right_input, self._right_output)
            sample['right_eye_sample'][:2] = self._right_output[:2]

        # Process bino gaze position
        if (_left_sample[13] and _right_sample[13] and
                (_bino_sample[0] is not np.nan and _bino_sample[1] is not np.nan)):
            self._bino_input = np.array([_bino_sample[0], _bino_sample[1]], dtype=np.float32)  # Convert to ndarray
            _flag_bino = self.filter_native_lib.do_filter_bino(self._bino_input, self._bino_output)
            sample['bino_gaze_position'][:2] = self._bino_output[:2]

        return sample


if __name__ == '__main__':

    import random


    def add_noise_to_samples(instances, noise_range=(-0.5, 0.5)):
        """
        Adds noise to the first two elements of left_eye_sample, right_eye_sample,
        and bino_gaze_position for each instance.

        Args:
            instances (list): A list of sample instances to modify.
            noise_range (tuple): A tuple specifying the range for random noise.
        """
        for instance in instances:
            # Add noise to left_eye_sample
            instance["left_eye_sample"][0] += random.uniform(*noise_range)
            instance["left_eye_sample"][1] += random.uniform(*noise_range)

            # Add noise to right_eye_sample
            instance["right_eye_sample"][0] += random.uniform(*noise_range)
            instance["right_eye_sample"][1] += random.uniform(*noise_range)

            # Add noise to bino_gaze_position
            instance["bino_gaze_position"][0] += random.uniform(*noise_range)
            instance["bino_gaze_position"][1] += random.uniform(*noise_range)


    # 创建初始样本
    _new_sample = {
        "left_eye_sample": [1, 2] + [1] * 12,
        "right_eye_sample": [1, 2] + [1] * 12,
        "bino_gaze_position": [1, 2],
        "timestamp": 123456,
    }

    # 生成12个样本的副本
    instances = [_new_sample.copy() for _ in range(12)]

    # 添加扰动
    add_noise_to_samples(instances)

    # 创建过滤器管理器
    filter_manager = Filter(look_ahead=2)

    # 对所有12个样本应用过滤器
    for i in range(12):
        _sample = filter_manager.filter_sample(instances[i])
        print(f"Sample {i + 1}: {_sample}")
