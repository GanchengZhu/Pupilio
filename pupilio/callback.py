
class CalibrationListener:
    """

    """

    def __init__(self):
        """

        """
        pass

    def on_calibration_target_onset(self, point_index):
        """

        """
        pass

    def on_calibration_over(self):
        """
        NOTE：

        感觉这个函数不是必须的
        `on_calibration_over`的代码完全可以`pupil_io.calibration_draw`后面执行
        """
        pass