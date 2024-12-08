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
# This demo shows how to configure the calibration process

# Author: GC Zhu
# Email: zhugc2016@gmail.com

import pygame
import pupilio

# use a custom config file to control the tracker
config = pupilio.DefaultConfig()

# Heuristic filter, default look_ahead = 2
config.look_ahead = 2

# Calibration: 2-point vs. 5-point
# The following usage methods are both correct, and only these four usage methods are allowed:
# config.cali_mode = pupilio.CalibrationMode.TWO_POINTS
# config.cali_mode = pupilio.CalibrationMode.FIVE_POINTS
# config.cali_mode = 2
# config.cali_mode = 5
config.cali_mode = 2

# Calibration target image and beep
config.cali_target_img = "cute_duck.png"
config.cali_target_beep = "duck_beep.wav"

# The calibration target image would zoom-in and -out, set the max and min image size here

config.cali_target_img_maximum_size = 120
config.cali_target_img_minimum_size = 60

# A cartoon face to assist users to adjust head position
# recommended size: 128 x 128 pixels
config.cali_smiling_face_img =  "cute_duck.png"
config.cali_frowning_face_img =  "cute_duck.png"

# Initialize the tracker
pupil_io = pupilio.Pupilio(config)

# create a task session, and set a session name
# If the session name contains spaces,
# it is recommended to replace them with underscores '_'.
pupil_io.create_session(session_name="quick_start")

# calibration and validation (recommended)
# set 'validate' to True if we would like to verify the calibration results
pupil_io.calibration_draw(validate=True, hands_free=False)

# start retrieving gaze
pupil_io.start_sampling()

# hang the main thread for 5 seconds by game
# eye tracking sampling are running on the background thread
pygame.time.wait(3 * 1000)

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
