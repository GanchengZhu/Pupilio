import pygame
from pupilio import Pupilio

# step 1: instantiate a connection to the tracker
pupil_io = Pupilio()

# step 2: create a task session, and set a session name
pupil_io.create_session(session_name="deepgaze_demo")

pygame.init()
scn_width, scn_height = (1920, 1080)
win = pygame.display.set_mode((scn_width, scn_height), FULLSCREEN|HWSURFACE)

# set 'validate' to True if you would like to verify the calibration results
deep_gaze.calibration_draw(validate=True)