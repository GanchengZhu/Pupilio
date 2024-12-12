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
# This demo shows how to read camera image while recording gaze data
# please do not use this function to capture high frame rate videos
# while recording gaze data

# Author: GC Zhu
# Email: zhugc2016@gmail.com

import os.path
import threading
import time

import cv2

import pupilio
from pupilio import Pupilio


class PreviewThread(threading.Thread):
    def __init__(self, pupil_io: Pupilio):
        threading.Thread.__init__(self)
        self._pupil_io = pupil_io
        self._is_running = True
        self.daemon = True

        self.preview_compression = [cv2.IMWRITE_JPEG_QUALITY, 40]  # ratio: 0~100
        self.preview_format = ".jpg"
        self.save_dir = "./data"
        os.makedirs(self.save_dir, exist_ok=True)

    def stop(self):
        self._is_running = False
        self.join()
        self._pupil_io = None

    def run(self):
        count = 0
        while self._is_running:
            time.sleep(0.016)
            preview_images = self._pupil_io.get_preview_images()
            cv2.imwrite(os.path.join(self.save_dir, f"left_camera_previewer_count_{count}{self.preview_format}"),
                        preview_images[0])
            cv2.imwrite(os.path.join(self.save_dir, f"right_camera_previewer_count_{count}{self.preview_format}"),
                        preview_images[1])
            count += 1
        print("Thread shutdown")


if __name__ == '__main__':
    pi = pupilio.Pupilio()
    preview_thread = PreviewThread(pupil_io=pi)
    preview_thread.start()
    pi.create_session("cali")
    pi.start_sampling()
    time.sleep(2)
    pi.stop_sampling()
    preview_thread.stop()
    pi.save_data("demo.csv")
    pi.release()
