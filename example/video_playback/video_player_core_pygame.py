#!/usr/bin/bash
# _*_ coding: utf-8 _*_

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
# This is a demo showing how to play video while recording gaze

import pygame
import os
import json
from pupilio import Pupilio
from pygame import FULLSCREEN, HWSURFACE, KEYDOWN
from pyvidplayer2 import Video
import tkinter as tk


# set SDL_VIDEODRIVER to windib
# os.environ['SDL_VIDEODRIVER'] = 'windib'

class VideoPlayer(object):
    """
    This class handles the playback and visualization of gaze in a single social video
    """

    def __init__(self, pupilio, screen):
        """
        'pupilio' is a tracker instance
        """
        self.pupilio = pupilio

        # a property for control video play, pause, stop/completed
        self.status = 0  # video playing status: 0-playing, 1-pause, 2-stop/completed

        # Define the clock for frame rate control
        self.clock = pygame.time.Clock()

        self._screen = screen

    def play(self, video_file, data_folder, show_gaze=False):
        """
        The main loop that control the playback of video/audio, and gaze
        """

        # make sure mixer is closed
        pygame.mixer.quit()

        # prepare the screen
        self._screen = pygame.display.get_surface()
        self._screen.fill((255,255,255))
        pygame.display.flip()

        # prepare the video
        _video = Video(f"./video/{video_file}")  # video path
        _video.change_resolution(1080)

        # create a new session for each video, so the sample data is saved in separate .csvs for each video
        _session_name = video_file.strip('.mp4')
        _session_name=_session_name.replace('-','_')
        self.pupilio.create_session(session_name=_session_name)

        # start sampling when the video is about to play
        self.pupilio.start_sampling()  # start sampling
        pygame.time.wait(100)  # sleep for 100 ms to capture some extra samples

        # start the video
        _video.play()
        _frame = 0
        while _video.active:
            for ev in pygame.event.get():
                if ev.type == KEYDOWN:
                    # pygame.quit()
                    pass

            # get the newest gaze position
            left, right, bino = self.pupilio.get_current_gaze()
            status, gx, gy = bino
            gx = int(gx)
            gy = int(gy)

            # Display the frame in the Pygame window
            self._screen.fill((255, 255, 255))
            if _video.draw(self._screen, (0, 0), force_draw=False):
                # pygame.display.update()

                # show the gaze cursor, if needed
                if show_gaze:
                    pygame.draw.circle(self._screen, (0, 255, 0), (gx, gy), 50, 5)  # cursor for the bino gaze
                pygame.display.flip()
            self.clock.tick(60)  # refresh the screen at 60 fps

            # send a trigger when the first frame appears on screen
            if _frame == 0:
                self.pupilio.set_trigger(101)
            # increase the frame count by one
            _frame +=1

        # when the video playback ends, send another trigger to mark this end
        self._screen.fill((255, 255, 255))
        pygame.display.flip()
        self.pupilio.set_trigger(201)

        # stop sampling when the video completes
        pygame.time.wait(100)  # sleep for 100 ms to capture ending samples
        self.pupilio.stop_sampling()  # stop sampling

        # save the sample data to file
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        _tmp_file_name = video_file.replace('.mp4', '.csv')
        self.pupilio.save_data(os.path.join(data_folder, _tmp_file_name))


def single_line_text(text, size):
    """
    text -- the text to show on screen
    size -- the font size for displaying a cross symbol on screen
    """

    if "microsoftyaheiui" in pygame.font.get_fonts():
        _font_name = "microsoftyaheiui"
    else:
        _font_name = pygame.font.get_fonts()[0]
    _font = pygame.font.SysFont(_font_name, size, bold=False, italic=False)
    _text = _font.render(text, True, (0,0,0))

    # show text on screen
    _screen = pygame.display.get_surface()
    _screen.fill((255, 255, 255))
    _screen.blit(_text, (_screen.get_width()//2- _text.get_width()//2,
                            _screen.get_height()//2 - _text.get_height()//2))
    pygame.display.flip()

def wait_key():
    """wait for a keypress, can be any key"""

    get_key = False
    while not get_key:
        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                get_key = True


# if __name__ == '__main__':
#
#
#
#     subj_folder = f"data/{participant_info['gender']}_{participant_info['subject_id']}"
#     os.makedirs(subj_folder, exist_ok=True)
#
#     # dump the subject information into a json file
#     with open(os.path.join(subj_folder, 'subj_info.json'), 'w') as subj:
#         json.dump(participant_info, subj)
#
#     show_gaze = participant_info['wears_glasses']
#
#     # initializing the tracker
#     deep_gaze = Pupilio()
#
#     # create a task session, and set a session name
#     # note that the "session name" will be used for logging by default
#
#     # calibrate the tracker, note that we need to create a session
#     deep_gaze.create_session(session_name="cali")
#
#     # window and graphics
#     # Initialize Pygame and set up the screen dimensions
#     pygame.init()
#     scn_width, scn_height = (1920, 1080)
#     screen = pygame.display.set_mode((scn_width, scn_height), FULLSCREEN|HWSURFACE)
#     # deep_gaze.calibration_draw(validate=True, hands_free=False, screen=screen)
#
#     videos = ["DSCF5292.mp4", "DSCF5289.mp4", "DSCF5269.mp4", "DSCF5260-2-t.mp4"]
#
#     # get the task ready
#     _vid = VideoAsd(deep_gaze, screen)
#
#     for vid in videos:
#         # show a fixation cross for 2 seconds
#         single_line_text(u"+", 64)
#         pygame.time.wait(2000)
#
#         # now play the video
#         _vid.play(vid, subj_folder, show_gaze)
#
#
#     # release the tracker instance
#     deep_gaze.release()
#
#     # show a fixation cross for 2 seconds
#     single_line_text(u"视频看完了，再见……", 64)
#     pygame.time.wait(2000)
#
#     # Quit Pygame after video playback
#     pygame.quit()
