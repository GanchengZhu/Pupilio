#!/usr/bin/env python

# Copyright (c) 2024, Hangzhou Deep Gaze Science and Technology Co., Ltd
# All Rights Reserved
#
# For use by  Hangzhou Deep Gaze Science and Technology Co., Ltd customers
# only. Redistribution and use in source and binary forms, with or without
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
# This is a demo showing how to use deep gaze pythonic library
# In this script, we connect to the tracker, perform a calibration, 
# validate the calibration results, then we subscribe to the sample data
# stream, with which we constantly update the position of a gaze cursor

# Author: Gancheng Zhu
# Last updated: 6/29/2025 by ZW

# Load libraries
import os
import time
import pygame
from pygame.locals import *
from pupilio import Pupilio, DefaultConfig
from pupilio.misc import *

# use the Pygame library for graphics, first init pygame and open a full screen window
pygame.init()
scn_width, scn_height = (1920, 1080)
win = pygame.display.set_mode((scn_width, scn_height), FULLSCREEN|HWSURFACE)

# use a custom config file to control the tracker
config = DefaultConfig()

# Heuristic filter, default look_ahead = 2 (i.e., a noisy spike is determined by
# 4 flanking samples)
config.look_ahead = 4
config.active_eye = 0  # 0--bino, -1 -- left eye only, 1 -- right eye only

# instantiate a tracker object
pupil_io = Pupilio(config)

# create a task session, and set a session name
# The session name must contain only letters, digits or underscores without any special characters.
pupil_io.create_session(session_name="deepgaze_demo")

# set 'validate' to True if you would like to verify the calibration results
pupil_io.calibration_draw(validate=True, hands_free=False, screen=win)

#  start retrieving gaze
pupil_io.start_sampling()
pygame.time.wait(100)  # sleep for 100 ms so the tracker cache some sample

# A free viewing task, in which we show a picture and overlay the gaze cursor
img_folder = 'images'
images = ['gray_grid.jpg', 'west_lake.jpg', 'old_town.jpg']

# show the images one by one in a loop, press a ENTER key to exit the program
for _img in images:
    # show the image on screen
    win.fill((128, 128, 128))
    im = pygame.image.load(os.path.join(img_folder, _img))
    win.blit(im, (0, 0))
    pygame.display.flip()
    # send a trigger to record in the eye movement data to mark picture onset
    pupil_io.set_trigger(202)

    # now lets show the gaze point, press any key to close the window
    got_key = False
    max_duration = 10000
    t_start = pygame.time.get_ticks()
    pygame.event.clear()  # clear all cached events if there were any
    gx, gy = -65536, -65536
    while not (got_key or (pygame.time.get_ticks() - t_start)>=max_duration):
        # get the newest gaze position
        left, right, bino = pupil_io.get_current_gaze()
        if pupil_io.config.active_eye == ActiveEye.BINO_EYE:
            status, gx, gy = bino
        if pupil_io.config.active_eye == ActiveEye.LEFT_EYE:
            status, gx, gy = left
        if pupil_io.config.active_eye == ActiveEye.RIGHT_EYE:
            status, gx, gy = right

        gx = int(gx)
        gy = int(gy)

        # check key presses
        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                if ev.key == K_RETURN:
                    got_key = True
                # if ev.key == K_SPACE:

        # update the visual (image and cursor)
        win.blit(im, (0,0))
        pygame.draw.circle(win, (0, 255, 0), (gx, gy), 50, 5)  # cursor for the left eye
        pygame.display.flip()

# stop sampling
pygame.time.wait(100)  # sleep for 100 ms to capture ending samples
pupil_io.stop_sampling()

# save the sample data to file
data_dir = "./data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

file_name = "deepgaze_demo.csv"
pupil_io.save_data(os.path.join(data_dir, file_name))

# release the tracker instance
pupil_io.release()

# quit pygame
pygame.quit()
