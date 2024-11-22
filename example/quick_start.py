# load PyGame library
import pygame
from pygame.locals import FULLSCREEN, HWSURFACE

# initialize PyGame
pygame.init()
# define the scree size
scn_width, scn_height = (1920, 1080)
# set a fullscreen mode with the above size
win = pygame.display.set_mode((scn_width, scn_height), FULLSCREEN|HWSURFACE)

# load Pupilio library
from pupilio import Pupilio

# instantiate a connection to the tracker
# set filter parameter: look_ahead
pupil_io = Pupilio(look_ahead=2)

# create a task session, and set a session name
# If the session name contains spaces,
# it is recommended to replace them with underscores '_'.
pupil_io.create_session(session_name="quick_start")

# calibration and validation (recommended)
# set 'validate' to True if we would like to verify the calibration results
pupil_io.calibration_draw(validate=True)

# start retrieving gaze
pupil_io.start_sampling()

# hang the main thread for 5 seconds by game
# eye tracking sampling are running on the background thread
pygame.time.wait(5 * 1000)

# stop eye tracking sampling
pupil_io.stop_sampling()

# sleep for 100 ms to capture ending samples
pygame.time.wait(100)

# save eye movement data
pupil_io.save_data("eye_movement.csv")

# release the tracker instance
# clean up Pupilio resources
pupil_io.release()

# quit pygame
pygame.quit()