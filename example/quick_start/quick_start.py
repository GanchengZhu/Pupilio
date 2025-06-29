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
# This script shows the most basic commands needed for an eye-tracking task

# load libraries
import pygame
from pygame.locals import FULLSCREEN, HWSURFACE
from pupilio import Pupilio

# initialize PyGame
pygame.init()

# scree size
scn_width, scn_height = (1920, 1080)

# open a window in fullscreen mode
win = pygame.display.set_mode((scn_width, scn_height), FULLSCREEN|HWSURFACE)

# Initialize the tracker
pupil_io = Pupilio()

# create a task session, and set a session name
# If the session name contains spaces,
# it is recommended to replace them with underscores '_'.
pupil_io.create_session(session_name="quick_start")

# calibration and validation (recommended)
# set 'validate' to True if we would like to verify the calibration results
pupil_io.calibration_draw(validate=True)

# start recording
pupil_io.start_sampling()

# Recording data for 5 seconds
msg = 'Recording... Script will terminate in 5 seconds.'
font = pygame.font.SysFont('Arial', 32)
_w, _h = font.size(msg)
txt = font.render(msg, True, (255,255,255))
win.fill((128,128,128))
win.blit(txt, ((scn_width - _w)//2, (scn_height - _h)//2))
pygame.display.flip()

pygame.time.wait(5 * 1000)

# stop recording
pupil_io.stop_sampling()

# sleep for 100 ms to capture ending samples
pygame.time.wait(100)

# save sample data to file
pupil_io.save_data("eye_movement.csv")

# release the tracker
pupil_io.release()

# quit pygame
pygame.quit()
