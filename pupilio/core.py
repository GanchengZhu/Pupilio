import ctypes
import logging
import os
import pathlib
import platform
import shutil
import threading
from datetime import datetime
from typing import Callable, List, Tuple

import numpy as np

from .event_detection import OnlineEventDetection
from .graphics import CalibrationUI
from .misc import ET_ReturnCode, TriggerHandler, Queue


def _sample_2_string(data):
    """
    :param data: dict, the format is
            data = {
                "trigger": trigger,
                "status": status,
                "left_eye_sample": left_eye_sample,
                "right_eye_sample": right_eye_sample,
                "timestamp": timestamp
            }
    :return: str, for csv file saving.
    """
    return (f"{data['timestamp']},{','.join(str(val) for val in data['left_eye_sample'])}," +
            f"{','.join(str(val) for val in data['right_eye_sample'])},{data['trigger']}\n")


class Pupilio:
    """Class for interacting with the eye tracker dynamic link library (DLL).
        A pythonic wrapper for Pupilio library."""

    def __init__(self):
        """
        Initialize the DeepGaze class.
        Load the appropriate DLL based on the platform (Windows or other).
        Set return types and argument types for DLL functions.
        Initialize various attributes and start the sampling thread.
        """

        # Determine the platform and load the appropriate DLL
        if platform.system().lower() == 'windows':
            _current_dir = os.path.abspath(os.path.dirname(__file__))
            _lib_dir = os.path.join(_current_dir, "lib")
            os.add_dll_directory(_lib_dir)
            os.environ['PATH'] = _lib_dir + ';' + os.environ['PATH']
            # dll
            _dll_path = os.path.join(_lib_dir, 'PupilioET.dll')
            self._et_native_lib = ctypes.CDLL(_dll_path, winmode=0)

        else:
            logging.warning("Not supported platform: %s" % platform.system())

        # Set return types for functions
        self._et_native_lib.deep_gaze_init.restype = ctypes.c_int
        self._et_native_lib.deep_gaze_face_pos.restype = ctypes.c_int
        self._et_native_lib.deep_gaze_cali.restype = ctypes.c_int
        self._et_native_lib.deep_gaze_est.restype = ctypes.c_int
        self._et_native_lib.deep_gaze_release.restype = ctypes.c_int
        self._et_native_lib.deep_gaze_est_lr.restype = ctypes.c_int

        # Set argument types for functions
        self._et_native_lib.deep_gaze_cali.argtypes = [ctypes.c_int]
        self._et_native_lib.deep_gaze_face_pos.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS')]
        self._et_native_lib.deep_gaze_est.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            ctypes.POINTER(ctypes.c_longlong)]
        self._et_native_lib.deep_gaze_est_lr.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            ctypes.POINTER(ctypes.c_longlong)]

        # Attributes for handling sampling and locking
        # Mutex lock for managing subscribers
        self._sample_subscriber_lock = threading.Lock()
        self._sample_subscribers: List[Callable] = []  # List to store subscriber functions
        self._sample_subscribers.append(self._write_sample)
        # Thread for sampling eye gaze
        self._sample_thread = None
        self._tmpSampleDataSteam = None
        self._tmpSampleDataPath = None
        self._workSpace = None
        self._sampling = False
        self._sampling_lock = threading.Lock()
        # Trigger handle for handling trigger
        self._trigger_handler = TriggerHandler()
        # Name for the current session
        self._session_name = None

        # Initialize DeepGaze, raise an exception if initialization fails
        if self._et_native_lib.deep_gaze_init() != ET_ReturnCode.ET_SUCCESS.value:
            raise Exception("DeepGaze init failed, please contact the developer!")

        self._face_pos = np.zeros(3, dtype=np.float32)
        self._pt = np.zeros(11, dtype=np.float32)
        self._pt_l = np.zeros(14, dtype=np.float32)
        self._pt_r = np.zeros(14, dtype=np.float32)

        self._online_event_detection = None

    def create_session(self, session_name: str) -> int:
        """
        Create a new session with the given name.
        Sets up directories, log files, and logger for the session.

        Args:
            session_name: Name of the session. For defining logging files and temporary files.

        Returns:
            int: ET_ReturnCode indicating the success or failure of session creation.
        """
        logging.info(f"Creating session: {session_name}")
        # Attributes for handling sampling and locking
        self._sampling = False
        # Trigger handle for handling trigger
        self._trigger_handler = TriggerHandler()
        # Name for the current session
        self._session_name = session_name

        self._online_event_detection = OnlineEventDetection()
        self._sample_subscribers.append(self._online_event_detection.handle_sample)

        # Thread for sampling eye gaze
        if not self._sample_thread:
            self._sample_thread = SampleThread(deep_gaze=self)
        else:
            self._sample_thread.running = False
            self._sample_thread = SampleThread(deep_gaze=self)
        self._sample_thread.start()  # Start the sampling thread

        self._workSpace = pathlib.Path.home().joinpath("Pupilio")

        if not self._workSpace.exists():
            self._workSpace.mkdir()

        # Set up the log directory
        _logDir = self._workSpace.joinpath("log")
        if not _logDir.exists():
            _logDir.mkdir()

        # Set up the temporary directory
        _tmpDir = self._workSpace.joinpath("tmp")
        if not _tmpDir.exists():
            _tmpDir.mkdir()

        # Set up the log file
        _logFile = _logDir.joinpath(f"log_{session_name}.txt")

        _currentTime = datetime.now()
        _timeString = _currentTime.strftime("%Y-%m-%d_%H-%M-%S")
        self._tmpSampleDataPath = _tmpDir.joinpath(f"tmp_{session_name}")
        self._tmpSampleDataSteam = self._tmpSampleDataPath.open("w", encoding="utf-8")
        self._tmpSampleDataSteam.write(
            "timestamp,left_eye_gaze_position_x,left_eye_gaze_position_y,left_eye_pupil_diameter_mm," +
            "left_eye_pupil_position_x,left_eye_pupil_position_y,left_eye_pupil_position_z," +
            "left_eye_visual_angle_theta,left_eye_visual_angle_phi," +
            "left_eye_visual_angle_vector_x,left_eye_visual_angle_vector_y," +
            "left_eye_visual_angle_vector_z,left_eye_pixels_per_degree_x,left_eye_pixels_per_degree_y," +
            "left_eye_valid,right_eye_gaze_position_x,right_eye_gaze_position_y,right_eye_pupil_diameter_mm," +
            "right_eye_pupil_position_x,right_eye_pupil_position_y,right_eye_pupil_position_z," +
            "right_eye_visual_angle_theta,right_eye_visual_angle_phi,right_eye_visual_angle_vector_x," +
            "right_eye_visual_angle_vector_y,right_eye_visual_angle_vector_z,right_eye_pixels_per_degree_x," +
            "right_eye_pixels_per_degree_y,right_eye_valid,trigger\n"
        )

        # Create a logger instance
        logger = logging.getLogger('')
        logger.setLevel(logging.DEBUG)

        # Create a file handler for logging to a file
        file_handler = logging.FileHandler(str(_logFile))
        file_handler.setLevel(logging.DEBUG)

        # Create a console handler for logging to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Define a logging format
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
            datefmt='%d-%b-%y %H:%M:%S')

        # Set the formatter for both file and console handlers
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the file and console handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return ET_ReturnCode.ET_SUCCESS.value

    def save_data(self, path: str) -> int:
        """
        Save sampled data to a file.

        Args:
            path (str): The path to save the data file.

        Returns:
            int: Return code indicating success or failure.
        """
        # Check if sampling is ongoing
        if not self._sampling:
            # Open the file and write the sampled data
            _content = b''
            with self._tmpSampleDataPath.open("rb") as f:
                _content = f.read()
            with open(path, 'wb') as f:
                f.write(_content)
            logging.info("save data to {}".format(path))
        else:
            logging.error("please call stop_sampling function.")
            raise Exception("please call stop_sampling function.")
        # Return success code if sampling is not ongoing
        return ET_ReturnCode.ET_SUCCESS.value

    def start_sampling(self) -> int:
        """
        Start eye gaze sampling.

        Returns:
            int: Return code indicating success or failure.
        """
        # Lock to ensure thread safety while modifying sampling status
        logging.info("start gaze sampling")
        with self._sampling_lock:
            self._sampling = True
        return ET_ReturnCode.ET_SUCCESS.value

    def get_sampling(self) -> bool:
        """
        Get the current sampling status.

        Returns:
            bool: True if sampling is ongoing, False otherwise.
        """
        # Lock to ensure thread safety while accessing sampling status
        with self._sampling_lock:
            return self._sampling

    def stop_sampling(self) -> int:
        """
        Stop eye gaze sampling.

        Returns:
            int: Return code indicating success or failure.
        """
        logging.info("stop gaze sampling")
        # Lock to ensure thread safety while modifying sampling status
        with self._sampling_lock:
            self._sampling = False
        return ET_ReturnCode.ET_SUCCESS.value

    def face_position(self) -> Tuple[int, np.ndarray]:
        """
        Get the current face position.

        Returns:
            tuple: A tuple containing the result code and numpy array of face position coordinates.
                   - If sampling is ongoing, returns ET_FAILED and an empty list.
                   - If successful, returns ET_SUCCESS and the face position coordinates.
        """
        # Create a ctypes array to store face position

        # Check if sampling is ongoing
        if self._sampling:
            # Return failed code if sampling is ongoing
            return ET_ReturnCode.ET_FAILED, self._face_pos
        # Call DLL function to get face position
        ret = self._et_native_lib.deep_gaze_face_pos(self._face_pos)
        # Return result code and face position coordinates
        return ret, self._face_pos

    def calibration(self, cali_point_id: int) -> int:
        """Perform calibration

        Args:
            cali_point_id (int): ID of the calibration point, 0 for the first calibration point,
                                 1 for the second, and so on.

        Returns:
            int: Result of the calibration, can be checked against ET_ReturnCode enum.
        """
        if self._sampling:
            return ET_ReturnCode.ET_FAILED
        return self._et_native_lib.deep_gaze_cali(cali_point_id)

    def estimation(self) -> Tuple[int, np.ndarray, int, int]:
        """
        Estimate the gaze state and position.

        Returns:
            tuple[int, np.ndarray, int, int]: A tuple containing ET_ReturnCode,
            eye position data, timestamp, and trigger.
        """
        timestamp = ctypes.c_longlong()
        status = self._et_native_lib.deep_gaze_est(self._pt.ctypes, ctypes.byref(timestamp))
        trigger = self._trigger_handler.get()
        return status, self._pt, timestamp.value, trigger

    def estimation_lr(self) -> Tuple[int, np.ndarray, np.ndarray, int, int]:
        timestamp = ctypes.c_longlong()
        status = self._et_native_lib.deep_gaze_est_lr(self._pt_l, self._pt_r, ctypes.byref(timestamp))
        trigger = self._trigger_handler.get()
        return status, self._pt_l, self._pt_r, timestamp.value, trigger

    def release(self) -> int:
        """
        Release the resources used by the eye tracker.

        Returns:
            int: ET_ReturnCode.ET_SUCCESS if successful.
        """
        logging.info("release deep gaze")
        if self._sample_thread:
            self._sample_thread.running = False
        if self._tmpSampleDataSteam:
            self._tmpSampleDataSteam.close()

        return_code = self._et_native_lib.deep_gaze_release()

        if platform.system().lower() == 'windows':
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            free_library = kernel32.FreeLibrary
            free_library.argtypes = [ctypes.c_void_p]
            if free_library(self._et_native_lib._handle):
                logging.info("native library unload successfully.")
            else:
                logging.info("failed to unload native library.")
        else:
            logging.warning("Not supported platform: %s" % platform.system())

        return return_code

    def set_trigger(self, trigger: int) -> int:
        """
        Set the trigger.

        Args:
            trigger: The trigger to set.
        """
        if isinstance(trigger, int) and 0 < trigger <= 255:
            self._trigger_handler.set(trigger)
            return ET_ReturnCode.ET_SUCCESS.value
        elif not isinstance(trigger, int):
            raise Exception("Trigger is not an integer value, please check the argument!")
        elif not (0 < trigger <= 255):
            raise Exception("Trigger must be an integer between 0 and 255, but given {}.".format(trigger))

    def _write_sample(self, data):
        """
        Write the example data.

        Args:
            data: The data to write.
        """
        self._tmpSampleDataSteam.write(_sample_2_string(data))
        self._tmpSampleDataSteam.flush()

    def calibration_draw(self, validate=False, bg_color=(255, 255, 255), hands_free=True):
        """
        Draw the indicator of the face distance and the eyebrow center position.
        Draw the calibration UI.
        Args:
            validate (bool): Whether to validate the calibration result.
            bg_color (tuple): Background color
            hands_free (bool): Whether to hands free
        """
        if not hands_free:
            CalibrationUI(deep_gaze=self).draw(validate=validate, bg_color=bg_color)
        else:
            CalibrationUI(deep_gaze=self).draw_hands_free(validate=validate, bg_color=bg_color)

    def subscribe_sample(self, *subscribers):
        """
        Subscribe a function to receive eye tracking sample.

            'sample' is an instance of dict. The format is as follows:

            sample = {
                "trigger": trigger,
                "status": status,
                "left_eye_sample": left_eye_sample,
                "right_eye_sample": right_eye_sample,
                "timestamp": timestamp
            }

            'left_eye_sample' is an instance of list, which contains 14 elements as follows:
                left_eye_sample[0]:left eye gaze position x (0~1920)
                left_eye_sample[1]:left eye gaze position y (0~1920)
                left_eye_sample[2]:left eye pupil diameter (0~10) (mm)
                left_eye_sample[3]:left eye pupil position x
                left_eye_sample[4]:left eye pupil position y
                left_eye_sample[5]:left eye pupil position z
                left_eye_sample[6]:left eye visual angle in spherical: theta
                left_eye_sample[7]:left eye visual angle in spherical: phi
                left_eye_sample[8]:left eye visual angle in vector: x
                left_eye_sample[9]:left eye visual angle in vector: y
                left_eye_sample[10]:left eye visual angle in vector: z
                left_eye_sample[11]:left eye pix per degree x
                left_eye_sample[12]:left eye pix per degree y
                left_eye_sample[13]:left eye valid (0:invalid 1:valid)
            'right_eye_sample' is an instance of list, which contains 14 elements as follows:
                right_eye_sample[0]:right eye gaze position x (0~1920)
                right_eye_sample[1]:right eye gaze position y (0~1920)
                right_eye_sample[2]:right eye pupil diameter (0~10) (mm)
                right_eye_sample[3]:right eye pupil position x
                right_eye_sample[4]:right eye pupil position y
                right_eye_sample[5]:right eye pupil position z
                right_eye_sample[6]:right eye visual angle in spherical: theta
                right_eye_sample[7]:right eye visual angle in spherical: phi
                right_eye_sample[8]:right eye visual angle in vector: x
                right_eye_sample[9]:right eye visual angle in vector: y
                right_eye_sample[10]:right eye visual angle in vector: z
                right_eye_sample[11]:right eye pix per degree x
                right_eye_sample[12]:right eye pix per degree y
                right_eye_sample[13]:right eye valid (0:invalid 1:valid)

        Args:
            *args (Callable): Functions to be unsubscribed.

        Raises:
            Exception: If any of the args are not Callable.

        Args:
            *args (Callable): Functions to be called when new eye tracking sample is available.

        Raises:
            Exception: If any of the args are not Callable.
        """
        with self._sample_subscriber_lock:
            for call in subscribers:
                if isinstance(call, Callable):
                    self._sample_subscribers.append(call)
                else:
                    raise Exception("Subscriber's args must be Callable")

    def unsubscribe_sample(self, *subscribers):
        """
        Unsubscribe functions from receiving eye tracking sample.
        """
        with self._sample_subscriber_lock:
            for call in subscribers:
                if isinstance(call, Callable):
                    if call in self._sample_subscribers:
                        self._sample_subscribers.remove(call)
                else:
                    raise Exception("Subscriber's args must be Callable")

    def subscribe_event(self, *args):
        """
        Subscribe a function to receive eye tracking sample.

        Raises:
            Exception: If any of the args are not Callable.
        """

        self._online_event_detection.subscribe(*args)
        pass

    def unsubscribe_event(self, *args):
        """
        Unsubscribe functions from receiving eye tracking sample.
        """

        self._online_event_detection.unsubscribe(*args)
        pass

    def clear_cache(self) -> int:
        """Clear the cache."""
        self._workSpace = pathlib.Path.home().joinpath("DeepGaze")
        if not self._workSpace.exists():
            shutil.rmtree(self._workSpace)
        return ET_ReturnCode.ET_SUCCESS.value

    @property
    def sample_subscriber_lock(self):
        return self._sample_subscriber_lock

    @property
    def sample_subscribers(self):
        return self._sample_subscribers


class SampleThread(threading.Thread):
    def __init__(self, pupil_io: Pupilio):
        """
        Initialize the SampleThread.

        Args:
            pupil_io (Pupilio): An instance of DeepGaze class.
        """
        threading.Thread.__init__(self)
        self._running = True  # Flag to indicate if the thread should keep running
        self.daemon = True
        self._pupil_io = pupil_io
        self._last_timestamp = 0
        self._cache_size = 2
        self._sample_cache: Queue = Queue(cache_size=self._cache_size)

    def run(self):
        """
        Main execution loop of the thread.
        """
        while self._running:
            # Check if sampling is enabled
            if self._pupil_io and self._pupil_io.get_sampling():
                try:
                    # Get eye tracking estimation results
                    _status, _left_eye_sample, _right_eye_sample, _timestamp, _trigger = self._pupil_io.estimation_lr()
                    if _trigger and self._last_timestamp == _timestamp:
                        # redefine the trigger at the tail of the cache
                        self._sample_cache.tail()["trigger"] = _trigger

                    if self._last_timestamp != _timestamp:
                        self._last_timestamp = _timestamp

                        if self._sample_cache.full():
                            # if the cache is full
                            # Notify all subscribers with the data
                            _sample = self._sample_cache.dequeue()
                            with self._pupil_io.sample_subscriber_lock:
                                for subscriber in self._pupil_io.sample_subscribers:
                                    subscriber(_sample)

                        # Prepare data dictionary
                        _new_sample = {
                            "status": _status,
                            # transform numpy array to native python dict
                            "left_eye_sample": _left_eye_sample.tolist(),
                            "right_eye_sample": _right_eye_sample.tolist(),
                            "timestamp": _timestamp,
                            "trigger": _trigger,
                        }
                        self._sample_cache.enqueue(_new_sample)

                except Exception as e:
                    # Handle any exceptions that might occur during estimation
                    logging.exception("sample callback function error: {}".format(e.args))

            elif not self._sample_cache.empty():
                # clear the data sample cache
                try:
                    _sample = self._sample_cache.dequeue()
                    with self._pupil_io.sample_subscriber_lock:
                        for subscriber in self._pupil_io.sample_subscribers:
                            subscriber(_sample)
                except Exception as e:
                    # Handle any exceptions that might occur during estimation
                    logging.exception("sample callback function error: {}".format(e))

    def stop_thread(self):
        """
        Stop the thread.
        """
        self._running = False  # Set running flag false to exit the loop


if __name__ == '__main__':
    pi = Pupilio()
