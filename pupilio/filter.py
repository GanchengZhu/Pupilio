import ctypes
import os
import platform
import threading
from collections import deque
from typing import Tuple, List, Callable

import numpy as np

from .misc import Queue


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

        self._filter_subscribers = []
        self._filter_subscriber_lock = threading.Lock()
        self._filter_timestamp_cache = Queue()

        # Initialize input and output arrays for left and right gaze
        self._left_input = np.zeros(2, dtype=np.float32)
        self._left_output = np.zeros(2, dtype=np.float32)

        self._right_input = np.zeros(2, dtype=np.float32)
        self._right_output = np.zeros(2, dtype=np.float32)

        self._timestamp_cache = deque()
        self._left_sample_cache = deque()
        self._right_sample_cache = deque()
        self._sample_cache = deque()
        self._n_drop = 2
        self._n_add_left_sample_filter = 0
        self._n_add_right_sample_filter = 0

    def filter_sample(self, sample):
        """
        Filter a sample of left and right gaze.

        :param sample
        :param left_gaze: List or tuple containing left gaze coordinates (x, y). If left gaze don't exist,
            please pass (np.nan, np.nan).
        :param _right_coordinate: List or tuple containing right gaze coordinates (x, y). See left_gaze
        :return: Tuple of filtered left and right gaze coordinates as lists
        """

        _timestamp = sample['timestamp']
        _left_coordinate = [np.nan, np.nan]
        _right_coordinate = [np.nan, np.nan]
        _left_sample = sample['left_eye_sample']
        _right_sample = sample['right_eye_sample']

        if _left_sample[13]:
            _left_coordinate[0] = _left_sample[0]
            _left_coordinate[1] = _left_sample[1]
        if _right_sample[13]:
            _right_coordinate[0] = _right_sample[0]
            _right_coordinate[1] = _right_sample[1]

        self._timestamp_cache.append(_timestamp)
        self._sample_cache.append(sample)
        _flag_left = False
        _flag_right = False

        if _left_coordinate[0] != np.nan:
            self._left_input[0] = _left_coordinate[0]
            self._left_input[1] = _left_coordinate[1]
            _flag_left = self.filter_native_lib.do_filter_left(self._left_input, self._left_output)
            if self._n_add_left_sample_filter < 4:
                self._n_add_left_sample_filter += 1
            else:
                self._left_sample_cache.append(self._left_output.tolist())

        elif not self._n_drop:
            self._left_sample_cache.append(_left_coordinate)

        if _right_coordinate[0] != np.nan:
            self._right_input[0] = _right_coordinate[0]
            self._right_input[1] = _right_coordinate[1]
            _flag_right = self.filter_native_lib.do_filter_right(self._right_input, self._right_output)
            if self._n_add_right_sample_filter < 4:
                self._n_add_right_sample_filter += 1
            else:
                self._right_sample_cache.append(self._right_output.tolist())
        elif not self._n_drop:
            self._right_sample_cache.append(_right_coordinate)

        # Call the filter functions with input and output array
        if self._n_drop > 0:
            # do noting except decrementing
            self._n_drop -= 1
            self._left_sample_cache.append(_left_coordinate)
            self._right_sample_cache.append(_right_coordinate)

        else:
            self.dispatch_sample(timestamp=self._timestamp_cache.popleft(),
                                 sample=self._sample_cache.popleft(),
                                 left_coordinate=self._left_sample_cache.popleft(),
                                 right_coordinate=self._right_sample_cache.popleft())

    def dispatch_sample(self, **kwargs):
        with self._filter_subscriber_lock:
            for subscriber in self._filter_subscribers:
                subscriber(**kwargs)

    def subscribe(self, *subscribers):
        with self._filter_subscriber_lock:
            for call in subscribers:
                if isinstance(call, Callable):
                    self._filter_subscribers.append(call)
                else:
                    raise Exception("Subscriber's args must be Callable")

    def unsubscribe(self, *subscribers):
        with self._filter_subscriber_lock:
            for call in subscribers:
                if isinstance(call, Callable):
                    if call in self._filter_subscribers:
                        self._filter_subscribers.remove(call)
                else:
                    raise Exception("Subscriber's args must be Callable")
