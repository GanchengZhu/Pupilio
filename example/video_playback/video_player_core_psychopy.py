
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

# Author: Gancheng Zhu
# Last updated: 10/28/2024 by ZW

import os
import sys
from psychopy import core, visual, event

class VideoPlayer(object):
    """
    This class handles the playback and visualization of gaze in a single social video-
    """

    def __init__(self, pi, win):
        """
        'pupilio' is a tracker instance
        win: A Psychopy window for video- playback
        """
        
        self.pi = pi
        self._win = win
        self.gaze_cursor = visual.Circle(win, radius=50, lineWidth=3, lineColor='green', units='pix')


    def _to_psychopy_coords(self, coords):
        """ convert a screen coords into the psychopy screen coords"""

        return [coords[0] - self._win.size[0] // 2, self._win.size[1] // 2 - coords[1]]


    def play(self, video_stim, video_file, data_folder, show_gaze=False):
        """
        The main loop that control the playback of video-/audio, and gaze

        video_stim: a psychopy video- object that has been loaded into the memory
        video_file: name of the video- being played
        data_folder: where to save the data files for this parcticular subject
        show_gaze: whether to show the gaze cursor
        """

        # create a new session for each video-, so the sample data is saved in separate .csvs for each video-
        _session_name = video_file.strip('.mp4')
        _session_name = _session_name.replace('-', '_')
        self.pi.create_session(session_name=_session_name)

        # start sampling when the video- is about to play
        self.pi.start_sampling()  # start sampling
        core.wait(0.1)  # sleep for 100 ms to capture some extra samples

        # show a fixation for 2.0 seconds
        fixation_stim = visual.TextStim(self._win, text='+', height=64, color=(-1,-1,-1), units='pix')
        fixation_stim.draw()
        self._win.flip()
        core.wait(2.0)

        # video_stim.play()
        _frame = 0
        while video_stim.status != visual.FINISHED:
            video_stim.draw()
            if show_gaze:
                left, right, bino = self.pi.get_current_gaze()
                status, gx, gy = bino
                self.gaze_cursor.pos = self._to_psychopy_coords((gx, gy))
                self.gaze_cursor.draw()
            self._win.flip()

            # hand key presses, if ESCAPE pressed, terminate the task
            if event.getKeys(keyList=['escape']):
                video_stim.stop()
                self.terminate_task(video_file, data_folder)

            if _frame == 0:
                self.pi.set_trigger(101)
            _frame += 1
        self.pi.set_trigger(201)

        # stop sampling when the video- completes
        core.wait(0.1)  # sleep for 100 ms to capture ending samples
        self.pi.stop_sampling()  # stop sampling
        core.wait(0.1)  # sleep for 100 ms to ensure the sampling is closed

        # save the sample data to file
        self.save_sample(video_file, data_folder)

    def save_sample(self, video_file, data_folder):
        # save the sample data to file
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        _tmp_file_name = video_file.replace('.mp4', '.csv')
        self.pi.save_data(os.path.join(data_folder, _tmp_file_name))

    def terminate_task(self, video_file, data_folder):
        """ terminate the task prematurely

        data_folder: provide a data folder so whatever data has collected so far will be saved,
        when a task terminates.
        """

        self.pi.stop_sampling()  # stop sampling
        self.pi.release()  # release the tracker object
        self.save_sample(video_file, data_folder)  # save the sample data to file
        core.quit()  # quit psychopy
        sys.exit()  # terminate the python session


if __name__ == '__main__':
    pass