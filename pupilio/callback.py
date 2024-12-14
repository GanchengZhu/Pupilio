class CalibrationListener:
    """
    A listener class to handle events during a calibration process. This class defines
    methods that can be overridden to perform specific actions when calibration or
    validation targets are presented during gaze calibration.

    Attributes:
        None

    Methods:
        __init__(): Initializes the listener instance.
        on_calibration_target_onset(point_index): Called when a calibration target is presented.
        on_validation_target_onset(point_index): Called when a validation target is presented.
    """

    def __init__(self):
        """
        Initializes the CalibrationListener instance.

        This method can be used to set up any initial state or parameters required for the listener.
        By default, it does nothing.
        """
        pass

    def on_calibration_target_onset(self, point_index):
        """
        This method is called when a calibration target is presented on the screen.

        Args:
            point_index (int): The index of the current calibration target. This can be used
            to identify the target's position or other characteristics specific to the calibration
            process.

        This method can be overridden to define actions that should occur when a calibration target
        is shown (e.g., logging, updating UI, or triggering an event).
        """
        pass

    def on_validation_target_onset(self, point_index):
        """
        This method is called when a validation target is presented on the screen.

        Args:
            point_index (int): The index of the current validation target. Similar to the calibration
            target, this can be used to identify the target's position or other properties related to
            the validation process.

        This method can be overridden to define actions that should occur when a validation target
        is shown (e.g., logging, updating UI, or triggering an event).
        """
        pass
