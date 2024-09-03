import logging
import threading
from typing import Callable

import numpy as np

from .filter import Filter
from .misc import Queue


class OnlineEventDetection:
    def __init__(self):
        self._sample_cache_size = 7
        self._velocity_cache_size = 10

        self._timestamp_cache = Queue(self._sample_cache_size)

        self._left_coordinate_cache = Queue(self._sample_cache_size)
        self._left_ppd_x_cache = Queue(self._sample_cache_size)
        self._left_ppd_y_cache = Queue(self._sample_cache_size)
        self._left_velocity_cache = Queue(self._velocity_cache_size)
        self._left_acceleration_cache = Queue(self._velocity_cache_size)

        self._right_coordinate_cache = Queue(self._sample_cache_size)
        self._right_ppd_x_cache = Queue(self._sample_cache_size)
        self._right_ppd_y_cache = Queue(self._sample_cache_size)
        self._right_velocity_cache = Queue(self._velocity_cache_size)
        self._right_acceleration_cache = Queue(self._velocity_cache_size)

        self._event_subscribers = []
        self._event_subscriber_lock = threading.Lock()
        self._filter_timestamp_cache = Queue()

        self._filter_instance = Filter()
        self._filter_instance.subscribe(self._detection)

        self._sr = 200  # sample rate
        self._velocity_timestamp_cache = Queue(self._velocity_cache_size)
        self._left_sample_res_cache = Queue(self._velocity_cache_size)
        self._right_sample_res_cache = Queue(self._velocity_cache_size)
        self._left_ppd_res_cache = Queue(self._velocity_cache_size)
        self._right_ppd_res_cache = Queue(self._velocity_cache_size)

    def handle_sample(self, sample: dict):
        """
        receive sample from core, send sample to filter
        """
        # print('handle sample')
        self._filter_instance.filter_sample(sample)

    def _detection(self, **kwargs):
        """
        receive samples from filter
        """
        # print('detection function')
        _timestamp = kwargs['timestamp']
        _sample = kwargs['sample']

        _left_ppd_x = _sample['left_eye_sample'][11]
        _left_ppd_y = _sample['left_eye_sample'][12]
        _left_gaze = kwargs['left_coordinate']

        _right_ppd_x = _sample['right_eye_sample'][11]
        _right_ppd_y = _sample['right_eye_sample'][12]
        _right_gaze = kwargs['right_coordinate']

        self._timestamp_cache.enqueue(_timestamp)

        self._left_coordinate_cache.enqueue(_left_gaze)
        self._left_ppd_x_cache.enqueue(_left_ppd_x)
        self._left_ppd_y_cache.enqueue(_left_ppd_y)

        self._right_coordinate_cache.enqueue(_right_gaze)
        self._right_ppd_x_cache.enqueue(_right_ppd_x)
        self._right_ppd_y_cache.enqueue(_right_ppd_y)

        if not self._left_coordinate_cache.full():
            return

        if self._velocity_timestamp_cache.full():
            self._velocity_timestamp_cache.dequeue()

            self._left_velocity_cache.dequeue()
            self._left_acceleration_cache.dequeue()
            self._left_sample_res_cache.dequeue()
            self._left_ppd_res_cache.dequeue()

            self._right_velocity_cache.dequeue()
            self._right_acceleration_cache.dequeue()
            self._right_sample_res_cache.dequeue()
            self._right_ppd_res_cache.dequeue()


        self._velocity_timestamp_cache.enqueue(self._timestamp_cache[2])
        self._left_sample_res_cache.enqueue(self._left_coordinate_cache[2])
        self._left_ppd_res_cache.enqueue((self._left_ppd_x_cache[2], self._left_ppd_y_cache[2]))
        self._right_sample_res_cache.enqueue(self._right_coordinate_cache[2])
        self._right_ppd_res_cache.enqueue((self._right_ppd_x_cache[2], self._right_ppd_y_cache[2]))

        # whether to interpolate
        if self._left_coordinate_cache[6][0] == np.nan and \
                self._left_coordinate_cache[7][0] != np.nan and \
                self._left_coordinate_cache[5][0] != np.nan:
            self._left_coordinate_cache[6][0] = 0.5 * (
                    self._left_coordinate_cache[5][0] + self._left_coordinate_cache[7][0])
            self._left_coordinate_cache[6][1] = 0.5 * (
                    self._left_coordinate_cache[5][1] + self._left_coordinate_cache[7][1])

        # contains np.nan in 5-sample
        # left eye blink detection
        _blink = False
        for i in range(5):
            if self._left_coordinate_cache[i][0] == np.nan:
                _blink = True
                break

        if _blink:
            # got a blin state, dequeue and now event type is in blink
            self._left_velocity_cache.enqueue(np.nan)
            self._left_acceleration_cache.enqueue(np.nan)


        else:  # not blink
            _x_0 = self._left_coordinate_cache[0][0]
            _x_1 = self._left_coordinate_cache[1][0]
            _x_2 = self._left_coordinate_cache[2][0]
            _x_3 = self._left_coordinate_cache[3][0]
            _x_4 = self._left_coordinate_cache[4][0]
            _ppd_x = self._left_ppd_x_cache[2]
            _current_velocity_x = self._sr * (
                    _x_4 + _x_3 - _x_1 - _x_0
            ) / (6 * _ppd_x + 1e-7)

            _current_acceleration_x = self._sr ** 2 * (
                    _x_4 - 2 * _x_2 + _x_0
            ) / (4 * _ppd_x + 1e-7)

            _y_0 = self._left_coordinate_cache[0][1]
            _y_1 = self._left_coordinate_cache[1][1]
            _y_2 = self._left_coordinate_cache[2][1]
            _y_3 = self._left_coordinate_cache[3][1]
            _y_4 = self._left_coordinate_cache[4][1]
            _ppd_y = self._left_ppd_y_cache[2]
            _current_velocity_y = self._sr * (
                    _y_4 + _y_3 - _y_1 - _y_0
            ) / (6 * _ppd_y + 1e-7)
            _current_acceleration_y = self._sr ** 2 * (
                    _y_4 - 2 * _y_2 + _y_0
            ) / (4 * _ppd_y + 1e-7)

            self._left_velocity_cache.enqueue(np.sqrt(_current_velocity_x ** 2 + _current_velocity_y ** 2))
            self._left_acceleration_cache.enqueue(
                np.sqrt(_current_acceleration_x ** 2 + _current_acceleration_y ** 2))

        # whether to interpolate
        if self._right_coordinate_cache[6][0] == np.nan and \
                self._right_coordinate_cache[7][0] != np.nan and \
                self._right_coordinate_cache[5][0] != np.nan:
            self._right_coordinate_cache[6][0] = 0.5 * (
                    self._right_coordinate_cache[5][0] + self._right_coordinate_cache[7][0])
            self._right_coordinate_cache[6][1] = 0.5 * (
                    self._right_coordinate_cache[5][1] + self._right_coordinate_cache[7][1])

        # contains np.nan in 5-sample
        # right eye blink detection
        _blink = False
        for i in range(5):
            if self._right_coordinate_cache[i][0] == np.nan:
                _blink = True
                break

        if _blink:
            # got a blin state, dequeue and now event type is in blink
            self._right_velocity_cache.enqueue(np.nan)
            self._right_acceleration_cache.enqueue(np.nan)

        else:  # not blink
            _x_0 = self._right_coordinate_cache[0][0]
            _x_1 = self._right_coordinate_cache[1][0]
            _x_2 = self._right_coordinate_cache[2][0]
            _x_3 = self._right_coordinate_cache[3][0]
            _x_4 = self._right_coordinate_cache[4][0]
            _ppd_x = self._right_ppd_x_cache[2]
            _current_velocity_x = self._sr * (
                    _x_4 + _x_3 - _x_1 - _x_0
            ) / (6 * _ppd_x + 1e-7)

            _current_acceleration_x = self._sr ** 2 * (
                    _x_4 - 2 * _x_2 + _x_0
            ) / (4 * _ppd_x + 1e-7)

            _y_0 = self._right_coordinate_cache[0][1]
            _y_1 = self._right_coordinate_cache[1][1]
            _y_2 = self._right_coordinate_cache[2][1]
            _y_3 = self._right_coordinate_cache[3][1]
            _y_4 = self._right_coordinate_cache[4][1]
            _ppd_y = self._right_ppd_y_cache[2]
            _current_velocity_y = self._sr * (
                    _y_4 + _y_3 - _y_1 - _y_0
            ) / (6 * _ppd_y + 1e-7)
            _current_acceleration_y = self._sr ** 2 * (
                    _y_4 - 2 * _y_2 + _y_0
            ) / (4 * _ppd_y + 1e-7)

            self._right_velocity_cache.enqueue(np.sqrt(_current_velocity_x ** 2 + _current_velocity_y ** 2))
            self._right_acceleration_cache.enqueue(
                np.sqrt(_current_acceleration_x ** 2 + _current_acceleration_y ** 2))

        self._timestamp_cache.dequeue()
        self._left_coordinate_cache.dequeue()
        self._left_ppd_x_cache.dequeue()
        self._left_ppd_y_cache.dequeue()
        self._right_coordinate_cache.dequeue()
        self._right_ppd_x_cache.dequeue()
        self._right_ppd_y_cache.dequeue()

        if self._velocity_timestamp_cache.full():
            self.dispatch_event(
                timestamp=self._velocity_timestamp_cache,
                left_velocity_cache=self._left_velocity_cache,
                right_velocity_cache=self._right_velocity_cache,
                left_acceleration_cache=self._left_acceleration_cache,
                right_acceleration_cache=self._right_acceleration_cache,
                left_gaze_cache=self._left_sample_res_cache,
                right_gaze_cache=self._right_sample_res_cache,
                left_ppd_cache=self._left_ppd_res_cache,
                right_ppd_cache=self._right_ppd_res_cache,
            )

    def dispatch_event(self, **kwargs):
        with self._event_subscriber_lock:
            try:
                for subscriber in self._event_subscribers:
                    subscriber(**kwargs)
            except Exception as e:
                logging.exception("event detection callback function error: {}".format(e))

    def subscribe(self, *subscribers):
        with self._event_subscriber_lock:
            for call in subscribers:
                if isinstance(call, Callable):
                    self._event_subscribers.append(call)
                else:
                    raise Exception("Subscriber's args must be Callable")

    def unsubscribe(self, *subscribers):
        with self._event_subscriber_lock:
            for call in subscribers:
                if isinstance(call, Callable):
                    if call in self._event_subscribers:
                        self._event_subscribers.remove(call)
                else:
                    raise Exception("Subscriber's args must be Callable")
