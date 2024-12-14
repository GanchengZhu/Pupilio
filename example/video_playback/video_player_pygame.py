
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

import json
import logging
import os
from datetime import datetime
import cv2
import pygame
import webview
from pygame.locals import FULLSCREEN, HWSURFACE

import video_player_core_pygame
from pupilio import Pupilio


def generate_thumbnail(video_path, thumbnail_path):
    """ generate video- thumbnails for menu displaying

    video_path: path to the video- file
    thumbnail_path: where to save the thumbnail
    """

    # open the video- file with openCV
    cap = cv2.VideoCapture(video_path)

    # retrieve the frame count for the video-
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # get a frame that is 1/10 into the video-
    frame_number = total_frames // 10
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if ret:
        # original frame  width and height
        height, width = frame.shape[:2]

        # keep the aspect ratio and resize the height to 480
        new_height = 480
        new_width = int(width * (new_height / height))  # 根据比例计算新宽度

        # thumbnail
        thumbnail = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

        # save the thumbnail
        cv2.imwrite(thumbnail_path, thumbnail)

    # release the video- capture
    cap.release()


class JsBridge:
    """ a webpage menu to set participant info"""

    def __init__(self):
        self._window = None
        _current_datetime = datetime.now()
        _current_time = _current_datetime.strftime("%Y_%m_%d_%H_%M_%S")
        # pat = {'name': name, 'gender': gender, 'age': age, 'task': task}
        self.expInfo = {
            "name": "",
            "age": "18",
            "gender": "male",
            "task": "[]",
            "show_gaze": 0,
            "now": _current_time
        }
        self.global_quit = False

    def set_window(self, window):
        """ select a window to use"""

        self._window = window

    def set_now(self, now):
        """ retrieve task time"""

        self.expInfo["now"] = now

    def set_test_item(self, item_id):
        """ select the task"""

        self.expInfo["task"] = item_id

    def set_participant_id(self, participant_id):
        """ give the subject an unique id"""

        self.expInfo["name"] = str(participant_id)

    def set_age(self, age):
        """ subject age"""

        self.expInfo["age"] = str(age)

    def set_gender(self, gender):
        """set the subject age (years) """

        self.expInfo["gender"] = gender

    def set_show_gaze(self, show_gaze):
        """whether the gaze cursor should be displayed"""

        self.expInfo["show_gaze"] = show_gaze

    def quit_all(self):
        """exit"""
        self._window.destroy()
        self.global_quit = True

    def get_video_dict(self):
        """ save all selected video- files into a dictionary"""

        return thumbnail_paths_dict

    def start_task(self):
        """Start the experiment here"""
        try:
            self._window.destroy()
        except Exception as e:
            logging.exception(e)
            self._window.destroy()


# the main task loop
if __name__ == '__main__':
    # video- file directory
    video_dir = 'video'
    # thumbnail directory
    thumbnail_dir = 'html/img'
    os.makedirs(thumbnail_dir, exist_ok=True)
    # get all the video- files
    video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    # a dictionary to save the video- file names
    thumbnail_paths_dict = {}

    # generate video- covers
    for video_file in video_files:
        video_path = os.path.join(video_dir, video_file)
        thumbnail_path = os.path.join(thumbnail_dir, f'{os.path.splitext(video_file)[0]}.png')

        # use the file name as key to save the thumbnails in a dictionary
        file_name = os.path.basename(thumbnail_path)
        thumbnail_paths_dict[os.path.split(video_path)[-1]] = f'img/{file_name}'

        if not os.path.exists(thumbnail_path):
            generate_thumbnail(video_path, thumbnail_path)

    # check if the filenames and paths are all correct
    for filename, path in thumbnail_paths_dict.items():
        print(f'{filename}: {path}')

    # now show the video- selection menu as a webpage
    bridge = JsBridge()
    html_url = 'html/par_info.html'
    # with open("item_choice.html", encoding='utf-8') as f:
    window = webview.create_window('Video Viewing Task', html_url, js_api=bridge, fullscreen=True)
    bridge.set_window(window)
    webview.start(debug=False, http_server=True)

    _current_datetime = datetime.now()
    _current_time = _current_datetime.strftime("%Y_%m_%d_%H_%M_%S")
    participant_info = bridge.expInfo

    """
    The return value of "participant_info"
    127.0.0.1 - - [26/Nov/2024 19:34:10] "GET /result_show.html HTTP/1.1" 200 5670
    {'name': '11', 'age': '11', 'gender': 'male', 'task': '["DSCF4652 00_00_00-00_00_12.avi", 
        "DSCF4696 00_00_06-00_00_28.avi", "DSCF4732 00_00_03-00_00_42.avi", "DSCF5250-1.avi",  
        "DSCF5253 00_00_06-00_00_41.avi", "DSCF5268 00_00_00-00_00_16.avi", 
        "DSCF5268 00_01_05-00_01_52.avi"]', 'now': '2024_11_26_19_33_53'}
    """

    # create a folder to store data collected from each participant
    subj_folder = f"data/{participant_info['name']}_{participant_info['age']}_{participant_info['gender']}"
    os.makedirs(subj_folder, exist_ok=True)

    # dump the subject information into a json file
    with open(os.path.join(subj_folder, 'subj_info.json'), 'w') as subj:
        json.dump(participant_info, subj)

    # debugging and set up task parameters
    show_gaze = participant_info['show_gaze']
    video_list = participant_info['task']
    # print("participant_info['task']: ", type(participant_info['task']))
    # print(show_gaze, 'show gaze')
    # print(video_list)
    # time.sleep(2)

    if len(video_list) == 0 or bridge.global_quit:
        print("No videos were selected or user pressed the `quit` button!")
        exit(0)

    # initializing the tracker
    pi = Pupilio()
    # window and graphics
    # Initialize Pygame and set up the screen dimensions
    pygame.init()
    scn_width, scn_height = (1920, 1080)
    screen = pygame.display.set_mode((scn_width, scn_height), FULLSCREEN|HWSURFACE)
    # deep_gaze.calibration_draw(validate=True, hands_free=False, screen=screen)

    # calibrate the tracker
    pi.create_session(session_name="cali")
    pi.calibration_draw(validate=True, hands_free=False, screen=screen)

    # get the task ready
    _vid = video_player_core_pygame.VideoPlayer(pi, screen)

    for vid in video_list:
        # show a fixation cross for 2 seconds
        video_player_core_pygame.single_line_text(u"+", 64)
        pygame.time.wait(2000)

        # now play the video
        _vid.play(vid, subj_folder, show_gaze)


    # release the tracker instance
    pi.release()
    # show a fixation cross for 2 seconds
    video_player_core_pygame.single_line_text(u"Playback completed...", 32)
    pygame.time.wait(2000)

    # Quit Pygame after video playback
    pygame.quit()
