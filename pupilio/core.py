import ctypes
import ipaddress
import logging
import os
import platform
import re
import sys
from typing import Callable, Tuple

import numpy as np

from .annotation import deprecated
from .misc import ET_ReturnCode


class Pupilio:
    """Class for interacting with the eye tracker dynamic link library (DLL).
        A pythonic wrapper for Pupilio library."""

    def __init__(self):
        """
        Initialize the Pupilio class.
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

        self._session_name = ""
        # Set return types
        self._et_native_lib.pupil_io_init.restype = ctypes.c_int
        self._et_native_lib.pupil_io_face_pos.restype = ctypes.c_int
        self._et_native_lib.pupil_io_cali.restype = ctypes.c_int
        self._et_native_lib.pupil_io_est.restype = ctypes.c_int
        self._et_native_lib.pupil_io_est_lr.restype = ctypes.c_int
        self._et_native_lib.pupil_io_release.restype = ctypes.c_int
        self._et_native_lib.pupil_io_get_version.restype = ctypes.c_char_p
        self._et_native_lib.pupil_io_get_previewer.restype = ctypes.c_int

        self._et_native_lib.pupil_io_previewer_init.restype = ctypes.c_int
        self._et_native_lib.pupil_io_previewer_start.restype = ctypes.c_int
        self._et_native_lib.pupil_io_previewer_stop.restype = ctypes.c_int

        self._et_native_lib.pupil_io_create_session.restype = ctypes.c_int
        self._et_native_lib.pupil_io_set_filter_enable.restype = ctypes.c_int
        self._et_native_lib.pupil_io_start_sampling.restype = ctypes.c_int
        self._et_native_lib.pupil_io_stop_sampling.restype = ctypes.c_int
        self._et_native_lib.pupil_io_sampling_status.restype = ctypes.c_int
        self._et_native_lib.pupil_io_send_trigger.restype = ctypes.c_int
        self._et_native_lib.pupil_io_save_data_to.restype = ctypes.c_int
        self._et_native_lib.pupil_io_clear_cache.restype = ctypes.c_int
        self._et_native_lib.pupil_io_get_current_gaze.restype = ctypes.c_int

        # Set argument types
        self._et_native_lib.pupil_io_cali.argtypes = [ctypes.c_int]
        self._et_native_lib.pupil_io_face_pos.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS')
        ]
        self._et_native_lib.pupil_io_est.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            ctypes.POINTER(ctypes.c_longlong)
        ]
        self._et_native_lib.pupil_io_est_lr.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            ctypes.POINTER(ctypes.c_longlong)
        ]
        self._et_native_lib.pupil_io_get_previewer.argtypes = [
            ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)),  # img_1
            ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)),  # img_2
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS')
        ]
        self._et_native_lib.pupil_io_previewer_init.argtypes = [ctypes.c_char_p, ctypes.c_int]
        self._et_native_lib.pupil_io_send_trigger.argtypes = [ctypes.c_int]
        self._et_native_lib.pupil_io_save_data_to.argtypes = [ctypes.c_char_p]
        self._et_native_lib.pupil_io_create_session.argtypes = [ctypes.c_char_p]

        self._et_native_lib.pupil_io_sampling_status.argtypes = [ctypes.POINTER(ctypes.c_bool)]
        self._et_native_lib.pupil_io_get_current_gaze.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS')
        ]

        version = self._et_native_lib.pupil_io_get_version()
        print("Native Pupilio Version:", version.decode("utf-8"))
        # Initialize Pupilio, raise an exception if initialization fails
        if self._et_native_lib.pupil_io_init() != ET_ReturnCode.ET_SUCCESS.value:
            raise Exception("Pupilio init failed, please contact the developer!")

        self._face_pos = np.zeros(3, dtype=np.float32)
        self._pt = np.zeros(11, dtype=np.float32)
        self._pt_l = np.zeros(14, dtype=np.float32)
        self._pt_r = np.zeros(14, dtype=np.float32)

        self._previewer_thread = None
        self._online_event_detection = None

    def previewer_start(self, udp_host: str, udp_port: int):
        """
        Initialize and start the previewer.

        :param udp_host: The UDP host address for receiving the video stream.
        :param udp_port: The UDP port number for receiving the video stream.

        This method first calls pupil_io_previewer_init to initialize the previewer,
        and then calls pupil_io_previewer_start to start the preview.
        """
        try:
            ipaddress.ip_address(udp_host)
        except ValueError:
            print(f"Invalid IP address: {udp_host}. Exiting.")
            sys.exit(1)  # Exit the program with an error status
        self._et_native_lib.pupil_io_previewer_init(udp_host.encode('utf-8'), udp_port)
        self._et_native_lib.pupil_io_previewer_start()

    def previewer_stop(self):
        """
        Stop the previewer.

        This method calls pupil_io_previewer_stop to cease receiving and processing
        the video stream.
        """
        self._et_native_lib.pupil_io_previewer_stop()

    def create_session(self, session_name: str) -> int:
        """
        Create a new session with the given name.
        Sets up directories, log files, and logger for the session.

        Args:
            session_name: Name of the session. For defining logging files and temporary files.
            The session name must contain only letters, digits or underscores without any special characters.

        Returns:
            int: ET_ReturnCode indicating the success or failure of session creation.
        """
        self._session_name = session_name
        available_session = bool(re.fullmatch(r'^[a-zA-Z0-9_]+$', session_name))
        if not available_session:
            raise Exception(
                f"Session name '{session_name}' is invalid. Ensure it includes only letters, digits, "
                f"or underscores without any special characters.")
        return self._et_native_lib.pupil_io_create_session(self._session_name.encode('utf-8'))

    def save_data(self, path: str) -> int:
        """
        Save sampled data to a file.

        Args:
            path (str): The path to save the data file.

        Returns:
            int: Return code indicating success or failure.
        """
        # Check if the directory exists and is writable
        directory = os.path.dirname(path)

        if not os.path.exists(directory):
            print(f"Directory does not exist: {directory}. Exiting.")
            sys.exit(1)  # Exit the program with an error status

        if not os.access(directory, os.W_OK):
            print(f"Directory is not writable: {directory}. Exiting.")
            sys.exit(1)  # Exit the program with an error status

        return self._et_native_lib.pupil_io_save_data_to(path.encode("utf-8"))

    def start_sampling(self) -> int:
        """
        Start eye gaze sampling.

        Returns:
            int: Return code indicating success or failure.
        """
        # Lock to ensure thread safety while modifying sampling status
        return self._et_native_lib.pupil_io_start_sampling()

    def get_sampling_status(self) -> bool:
        """
        Check the status of sampling from the pupil IO.

        Returns:
        bool: True if sampling is active, False otherwise.
        """
        # Create a c_bool variable to hold the status
        status = ctypes.c_bool()

        # Create a pointer to the c_bool variable
        status_pointer = ctypes.byref(status)

        # Call the function from the C library
        self._et_native_lib.pupil_io_sampling_status(status_pointer)

        # Return the value of the status
        return status.value

    def stop_sampling(self) -> int:
        """
        Stop eye gaze sampling.

        Returns:
            int: Return code indicating success or failure.
        """
        return self._et_native_lib.pupil_io_stop_sampling()

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
        if self.get_sampling_status():
            # Return failed code if sampling is ongoing
            return ET_ReturnCode.ET_FAILED, self._face_pos
        # Call DLL function to get face position
        ret = self._et_native_lib.pupil_io_face_pos(self._face_pos)
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
        if self.get_sampling_status():
            return ET_ReturnCode.ET_FAILED
        return self._et_native_lib.pupil_io_cali(cali_point_id)

    @deprecated("1.1.1")
    def estimation(self) -> Tuple[int, np.ndarray, int, int]:
        """
        Estimate the gaze state and position.

        Returns:
            tuple[int, np.ndarray, int, int]: A tuple containing ET_ReturnCode,
            eye position data, timestamp, and trigger.
        """
        timestamp = ctypes.c_longlong()
        status = self._et_native_lib.pupil_io_gaze_est(self._pt.ctypes, ctypes.byref(timestamp))
        trigger = 0
        return status, self._pt, timestamp.value, trigger

    def estimation_lr(self) -> Tuple[int, np.ndarray, np.ndarray, int, int]:
        """
        Estimate the gaze state and position for left and right eyes.

        This function calls the native pupil estimation library to obtain the
        estimated gaze points for both the left and right eyes, as well as the
        timestamp of the estimation. The function returns the status of the
        operation, the gaze points for the left and right eyes, the timestamp,
        and an additional trigger value.

        Returns:
            Tuple[int, np.ndarray, np.ndarray, int, int]:
                - int: Status code, where `ET_ReturnCode.ET_SUCCESS` indicates success.
                - np.ndarray: Estimated gaze point for the left eye. Contains 14 elements.
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
                - np.ndarray: Estimated gaze point for the right eye. Contains 14 elements.
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
                - int: Timestamp of the estimation (in milliseconds).
                - int: Trigger value, initialized to 0.
        Example:
            status, left_eye_sample, right_eye_sample, timestamp, trigger = instance.estimation_lr()
            if status == ET_ReturnCode.ET_SUCCESS:
                print("Gaze estimation successful.")
        """
        timestamp = ctypes.c_longlong()
        status = self._et_native_lib.pupil_io_est_lr(self._pt_l, self._pt_r, ctypes.byref(timestamp))
        trigger = 0
        return status, self._pt_l, self._pt_r, timestamp.value, trigger

    def release(self) -> int:
        """
        Release the resources used by the eye tracker.

        Returns:
            int: ET_ReturnCode.ET_SUCCESS if successful.
        """
        logging.info("release deep gaze")
        return_code = self._et_native_lib.pupil_io_release()

        # if platform.system().lower() == 'windows':
        #     kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        #     free_library = kernel32.FreeLibrary
        #     free_library.argtypes = [ctypes.c_void_p]
        #     if free_library(self._et_native_lib._handle):
        #         logging.info("native library unload successfully.")
        #     else:
        #         logging.info("failed to unload native library.")
        # else:
        #     logging.warning("Not supported platform: %s" % platform.system())
        return return_code

    def set_trigger(self, trigger: int) -> int:
        """
        Set the trigger.

        Args:
            trigger: The trigger to set.
        """
        return self._et_native_lib.pupil_io_send_trigger(trigger)

    def set_filter_enable(self, status: bool) -> int:
        """
        Enable or disable the filter.

        Args:
            status (bool): True to enable the filter, False to disable.
        """
        return self._et_native_lib.pupil_io_set_filter_enable(status)

    def get_current_gaze(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Retrieve the current gaze values for the left eye, right eye, and binocular gaze.

        Example:
            left, right, bino = pupil_io.get_current_gaze()
            left_valid = left[0]
            right_valid = right[0]
            bino_valid = bino[0]
            left_coordinate_x, left_coordinate_y = left[1], left[2]
            right_coordinate_x, right_coordinate_y = right[1], right[2]
            bino_coordinate_x, bino_coordinate_y = bino[1], bino[2]
        Returns:
            np.ndarray: A Tuple containing the left gaze, right gaze, and binocular gaze as floats.
        """
        # Create NumPy float arrays to hold the gaze values
        left_gaze = np.zeros(3, dtype=np.float32)
        right_gaze = np.zeros(3, dtype=np.float32)
        bino_gaze = np.zeros(3, dtype=np.float32)

        # Call the C function
        self._et_native_lib.pupil_io_get_current_gaze(
            left_gaze,  # Pointer to left gaze
            right_gaze,  # Pointer to right gaze
            bino_gaze  # Pointer to binocular gaze
        )
        # Return the gaze values as a NumPy array
        return left_gaze, right_gaze, bino_gaze

    def calibration_draw(self, screen=None, validate=False, bg_color=(255, 255, 255), hands_free=True):
        """
        Draw the indicator of the face distance and the eyebrow center position.
        Draw the calibration UI.
        Args:
            screen: The screen to draw on. You can choose pygame window or psychopy window
            validate (bool): Whether to validate the calibration result.
            bg_color (tuple): Background color, specific parameter for pygame
            hands_free (bool): Whether to hands free
        """
        from pygame import Surface
        screen_type = ""
        if screen is None:
            try:
                import pygame
                from pygame.locals import FULLSCREEN, HWSURFACE
                pygame.init()
                scn_width, scn_height = (1920, 1080)
                screen = pygame.display.set_mode((scn_width, scn_height), FULLSCREEN | HWSURFACE)
                screen_type = 'pygame'
            except:
                print("The parameter passed is None, creating a new pygame screen.")
                raise Exception("pygame screen can't be created.")
        elif isinstance(screen, Surface):
            screen_type = 'pygame'
        else:
            from psychopy.visual import Window
            if isinstance(screen, Window):
                screen_type = 'psychopy'

        if screen_type == "":
            raise Exception("Screen cannot be None. Please pass pygame window or psychopy window instance")

        if screen_type == 'pygame':
            from .graphics_pygame import CalibrationUI
        else:
            from .graphics import CalibrationUI

        if not hands_free:
            CalibrationUI(pupil_io=self, screen=screen).draw(validate=validate, bg_color=bg_color)
        else:
            CalibrationUI(pupil_io=self, screen=screen).draw_hands_free(validate=validate, bg_color=bg_color)

    @deprecated("1.1.2")
    def subscribe_sample(self, subscriber_func: Callable, args=(), kwargs=None):
        """
        Subscribe a function to receive eye tracking samples.

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
            subscriber_func (Callable): The function to be called when a new eye tracking sample is available.
            args (tuple): Optional positional arguments to pass to the subscriber function.
            kwargs (dict): Optional keyword arguments to pass to the subscriber function.

        Raises:
            Exception: If `subscriber_func` is not Callable.
        """
        if kwargs is None:
            kwargs = {}

    @deprecated("1.1.2")
    def unsubscribe_sample(self, subscriber_func: Callable, args=(), kwargs=None):
        """
        Unsubscribe a function from receiving eye tracking samples.

        Args:
            subscriber_func (Callable): The function to be removed from subscribers.
            args (tuple): Positional arguments used for subscription (should match what was used during subscription).
            kwargs (dict): Keyword arguments used for subscription (should match what was used during subscription).

        Raises:
            Exception: If `subscriber_func` is not Callable.
        """
        if kwargs is None:
            kwargs = {}

    @deprecated("1.1.2")
    def subscribe_event(self, *args):
        """
        Subscribe a function to receive eye tracking sample.

        Raises:
            Exception: If any of the args are not Callable.
        """

        # self._online_event_detection.subscribe(*args)
        pass

    @deprecated("1.1.2")
    def unsubscribe_event(self, *args):
        """
        Unsubscribe functions from receiving eye tracking sample.
        """

        # self._online_event_detection.unsubscribe(*args)
        pass

    def clear_cache(self) -> int:
        """Clear the cache."""
        return self._et_native_lib.pupil_io_clear_cache()

    @deprecated("1.1.2")
    @property
    def sample_subscriber_lock(self):
        return None

    @deprecated("1.1.2")
    @property
    def sample_subscribers(self):
        return None
