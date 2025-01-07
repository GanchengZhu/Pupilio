import pygame
from pygame.locals import FULLSCREEN, HWSURFACE

import pupilio

from pupilio.callback import CalibrationListener


class MyListener(CalibrationListener):
    def __init__(self):
        super().__init__()
        print("init")

    def on_calibration_target_onset(self, point_index):
        print(f"target onset with the index of {point_index}")


if __name__ == '__main__':
    # use a custom config file to control the tracker
    config = pupilio.DefaultConfig()
    my_listener = MyListener()
    config.calibration_listener = my_listener

    # initialize PyGame
    pygame.init()

    # scree size
    scn_width, scn_height = (1920, 1080)

    # open a window in fullscreen mode
    win = pygame.display.set_mode((scn_width, scn_height), FULLSCREEN | HWSURFACE)

    # Initialize the tracker
    pupil_io = pupilio.Pupilio(config)

    # create a task session, and set a session name
    # If the session name contains spaces,
    # it is recommended to replace them with underscores '_'.
    pupil_io.create_session(session_name="quick_start")

    # calibration and validation (recommended)
    # set 'validate' to True if we would like to verify the calibration results
    pupil_io.calibration_draw(validate=False, hands_free=False)
    """
    NOTE:
    `on_calibration_over` 不是必须的, `on_calibration_over`的代码完全可以`pupil_io.calibration_draw`后面执行。
    """

    # start retrieving gaze
    pupil_io.start_sampling()

    # Recording data for 5 seconds
    msg = 'Recording... Script will terminate in 5 seconds.'
    font = pygame.font.SysFont('Arial', 32)
    _w, _h = font.size(msg)
    txt = font.render(msg, True, (0, 0, 0))
    win.fill((128, 128, 128))
    win.blit(txt, ((scn_width - _w) // 2, (scn_height - _h) // 2))
    pygame.display.flip()

    pygame.time.wait(5 * 1000)

    # stop eye tracking sampling
    pupil_io.stop_sampling()

    # sleep for 100 ms to capture ending samples
    pygame.time.wait(100)

    # save eye movement data
    pupil_io.save_data("eye_movement.csv")

    # release the tracker
    pupil_io.release()

    # quit pygame
    pygame.quit()
