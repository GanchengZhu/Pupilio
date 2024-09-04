#!/usr/bin/env python

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
# This is a demo showing how to use deep gaze pythonic library
# In this script, we connect to the tracker, perform a calibration,
# validate the calibration results, then we subscribe to the sample data
# stream, with which we contantly update the position of a gaze cursor

# Author: Gancheng Zhu
# Last updated: 4/11/2024

# Load libraries
import os
import pygame
from pygame.locals import FULLSCREEN, HWSURFACE, K_RETURN, KEYDOWN
from pupilio import Pupilio

# step 1: instantiate a connection to the tracker
pupil_io = Pupilio()

# step 2: create a task session, and set a session name
# note that the "session name" will be used for logging by default
pupil_io.create_session(session_name="pupilio_demo")

# step 3: calibration and validation (optional)
# for simplicity and minimal dependency, we use the Pygame library for
# graphics, first init pygame and open a full screen window
pygame.init()
scn_width, scn_height = (1920, 1080)
win = pygame.display.set_mode((scn_width, scn_height), FULLSCREEN|HWSURFACE)

# set 'validate' to True if you would like to verify the calibration results
pupil_io.calibration_draw(validate=True)

# step 4: create subscribers (callable function) to listen to the eye tracking data streams
# one can subscribe to either the sample, event data stream, or both
# NOTE: DO NOT include time-consuming operations (those take more than 5 milliseconds)
# in a subscriber, as this may decrease the eye tracking frame rate.
#
# here we show how to subscribe to the sample data stream, first instantiate a global
# varible to store the current left- and right-eye gaze position
newest_gaze = [0, 0, 0, 0]

def sample_subscriber(sample):
    """
    In this subscriber, we retrieve the left- and right- gaze position (in screen
    pixel coordinates, and use it to update the global variable newest_gaze)

    'sample' is an instance of dict. The format is as follows:
    sample = {
        "marker": marker, # current received marker, if not exists, marker will be -1
        "status": status, # status of eye tracking devices, see ETReturn_Code
        "gaze_sample": gaze_sample,
        "timestamp": timestamp
        }

    'gaze_sample' is a list, which contains 11 elements as follows:
         gaze_sample[0]: left eye gaze position x (0~1920)
         gaze_sample[1]: left eye gaze position y (0~1080)
         gaze_sample[2]: left eye pupil size (0~10) (mm)
         gaze_sample[3]: right eye gaze position x (0~1920) pix
         gaze_sample[4]: right eye gaze position y (0~1080) pix
         gaze_sample[5]: right eye pupil size (0~10) (mm)
         gaze_sample[6]: pixels per degree X
         gaze_sample[7]: pixels per degree Y
         gaze_sample[8]: flag norm:0; miss left eye:1;miss right eye:2;no eyes:3
         gaze_sample[9]: bino gaze position x (0~1920) pix
         gaze_sample[10]:bino gaze position y (0~1920) pix
    """

    newest_gaze[0] = sample['left_eye_sample'][0]
    newest_gaze[1] = sample['left_eye_sample'][1]
    newest_gaze[2] = sample['right_eye_sample'][0]
    newest_gaze[3] = sample['right_eye_sample'][1]

# step 5: subscript to the sample stream using the above deifned sample_subscriber
pupil_io.subscribe_sample(sample_subscriber)

# step 6: start retrieving gaze
pupil_io.start_sampling()
pygame.time.wait(100)  # sleep for 100 ms so the tracker cache some some sample

# step 7: A free viewing task, in which we show a picture and overlay the gaze cursor

img_folder = 'images'
images = ['lenna.png', 'lenna_gray.png']

# show the images one by one in a loop, press a ENTER key to exit the program
for _img in images:
    # step 7.1: show a fixation on screen
    win.fill((128, 128, 128))
    pygame.draw.line(win, (0, 255, 0), (scn_width//2 - 20, scn_height//2),
                     (scn_width//2 + 20, scn_height//2), 3)
    pygame.draw.line(win, (0, 255, 0), (scn_width//2, scn_height//2 - 20),
                     (scn_width//2, scn_height//2 + 20), 3)
    pygame.display.flip()
    # send a trigger to record in the eye movemen data to mark fixation onset
    # a trigger could be an integer between 1-255
    pupil_io.set_trigger(201)
    # show the fixation for 1 sec
    pygame.time.wait(1000)

    # step 7.2: show the image on screen
    im = pygame.image.load(os.path.join(img_folder, _img))
    win.blit(im, (0,0))
    pygame.display.flip()
    # send a trigger to record in the eye movemen data to mark picture onset
    pupil_io.set_trigger(202)

    # now lets show the gaze point, press any key to close the window
    got_key = False
    max_duration = 5000
    t_start = pygame.time.get_ticks()
    while not (got_key or (pygame.time.get_ticks() - t_start)>=5000):
        # get the newest gaze position
        lx = int(newest_gaze[0])
        ly = int(newest_gaze[1])
        rx = int(newest_gaze[2])
        ry = int(newest_gaze[3])
        # check key presses
        for ev in pygame.event.get():
            if (ev.type == KEYDOWN):
                if ev.key == K_RETURN:
                    got_key = True
                # if ev.key == K_SPACE:

        # update the visual (image and cursor)
        win.blit(im, (0,0))
        pygame.draw.circle(win, (0, 0, 255), (rx, ry), 25)
        pygame.display.flip()

# step 8: stop sampling
pupil_io.stop_sampling()
pygame.time.wait(100)  # sleep for 100 ms to capture ending samples

# step 9: save the sample data to file
data_dir = "./data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

file_name = "pupil_io_demo.csv"
pupil_io.save_data(os.path.join(data_dir, file_name))

# step 10: release the tracker instance
pupil_io.release()

# quit pygame
pygame.quit()