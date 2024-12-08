# _*_ coding: utf-8 _*_
# Author: GC Zhu
# Email: zhugc2016@gmail.com
import ctypes
import os.path
import threading
import time

import cv2
import numpy as np

import pupilio
from pupilio import Pupilio, ET_ReturnCode


class PreviewThread(threading.Thread):
    def __init__(self, pupil_io: Pupilio):
        threading.Thread.__init__(self)
        self._pupil_io = pupil_io
        self._is_running = True
        self.daemon = True
        self.IMG_HEIGHT, self.IMG_WIDTH = 1024, 1280

        # preview retrieving
        self._preview_img_1 = np.zeros((self.IMG_HEIGHT, self.IMG_WIDTH), dtype=np.uint8)
        self._preview_img_2 = np.zeros((self.IMG_HEIGHT, self.IMG_WIDTH), dtype=np.uint8)
        self._eye_rects = np.zeros(4 * 4, dtype=np.float32)  # 4个眼睛矩形
        self._pupil_centers = np.zeros(4 * 2, dtype=np.float32)  # 4个瞳孔中心
        self._glint_centers = np.zeros(4 * 2, dtype=np.float32)  # 4个闪光中心

        self.preview_compression = [cv2.IMWRITE_JPEG_QUALITY, 40]  # ratio: 0~100
        self.preview_format = ".jpg"
        self.save_dir = "./data"
        os.makedirs(self.save_dir, exist_ok=True)

    def stop(self):
        self._is_running = False
        self.join()

    def run(self):
        count = 0
        while self._is_running:
            img_1_ptr = self._preview_img_1.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
            img_2_ptr = self._preview_img_2.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))

            result = self._pupil_io._et_native_lib.deep_gaze_get_previewer(ctypes.pointer(img_1_ptr),
                                                                           ctypes.pointer(img_2_ptr),
                                                                           self._eye_rects, self._pupil_centers,
                                                                           self._glint_centers)

            ctypes.memmove(self._preview_img_1.ctypes.data, img_1_ptr, self._preview_img_1.nbytes)
            ctypes.memmove(self._preview_img_2.ctypes.data, img_2_ptr, self._preview_img_2.nbytes)

            if result == ET_ReturnCode.ET_SUCCESS:
                combined_image = self.process_images(self._preview_img_1, self._preview_img_2,
                                                     self._eye_rects, self._pupil_centers, self._glint_centers)
                cv2.imwrite(os.path.join(self.save_dir, f"count_{count}{self.preview_format}"), combined_image)
                count += 1

    def process_images(self, img1: np.ndarray, img2: np.ndarray, eye_rects: np.ndarray,
                       pupil_centers: np.ndarray, glint_centers: np.ndarray) -> np.ndarray:
        imgs = [img1, img2]
        rects = [
            [eye_rects[:4], eye_rects[4:8]],
            [eye_rects[8:12], eye_rects[12:16]]
        ]
        pupil_center_list = [
            [pupil_centers[0:2], pupil_centers[2:4]],
            [pupil_centers[4:6], pupil_centers[6:8]]
        ]
        glint_center_list = [
            [glint_centers[0:2], glint_centers[2:4]],
            [glint_centers[4:6], glint_centers[6:8]]
        ]

        for n, img in enumerate(imgs):
            for m, eye_rect in enumerate(rects[n]):
                x, y, w, h = eye_rect
                cv2.rectangle(img, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2)

                pupil_center = tuple(map(int, pupil_center_list[n][m]))
                glint_center = tuple(map(int, glint_center_list[n][m]))

                cv2.circle(img, pupil_center, 5, (0, 255, 0), -1)
                cv2.circle(img, glint_center, 5, (0, 255, 0), -1)

            imgs[n] = cv2.resize(img, (320, 256))
        return np.hstack(imgs)


if __name__ == '__main__':
    pi = pupilio.Pupilio()
    pt = PreviewThread(pupil_io=pi)
    pt.start()
    pi.create_session("cali")
    pi.start_sampling()
    time.sleep(2)
    pi.stop_sampling()
    pi.save_data("demo.csv")
    # do something
