"""
how to use deep gaze pythonic library
"""
import os
import random
import time

import numpy as np
import pygame

# step 1: load DeepGaze module
from deepgaze import DeepGaze
from deepgaze.filter import Filter

# step 2: instantiate DeepGaze
deep_gaze = DeepGaze()

# step 3: create a task session with passing an argument of session name
deep_gaze.create_session(session_name="example")

gaze_right = [0, 0]


def subscribe_1(data):
    # print(data)
    pass


def subscribe_2(data):
    """
    'data' is an instance of dict. The format is as follows:
            data = {
                "trigger": trigger,
                "status": status,
                "left_eye_sample": left_eye_sample,
                "right_eye_sample": right_eye_sample,
                "timestamp": timestamp
            }
    'left_eye_sample' is an instance of list, which contains 14 elements as follows:
        left_eye_sample[0]:left eye gaze position x (0~1920)
        left_eye_sample[1]:left eye gaze position y (0~1920)
        left_eye_sample[2]:left eye pupil diameter (0~10) (mm)
        left_eye_sample[3]:left eye pupil position x
        left_eye_sample[4]:left eye pupil position y
        left_eye_sample[5]:left eye pupil position z
        left_eye_sample[6]:left eye visual angle in spherical: theta
        left_eye_sample[7]:left eye visual angle in spherical: phi
        left_eye_sample[8]:left eye visual angle in vector: x
        left_eye_sample[9]:left eye visual angle in vector: y
        left_eye_sample[10]:left eye visual angle in vector: z
        left_eye_sample[11]:left eye pix per degree x
        left_eye_sample[12]:left eye pix per degree y
        left_eye_sample[13]:left eye valid (0:invalid 1:valid)
    'right_eye_sample' is an instance of list, which contains 14 elements as follows:
        right_eye_sample[0]:right eye gaze position x (0~1920)
        right_eye_sample[1]:right eye gaze position y (0~1920)
        right_eye_sample[2]:right eye pupil diameter (0~10) (mm)
        right_eye_sample[3]:right eye pupil position x
        right_eye_sample[4]:right eye pupil position y
        right_eye_sample[5]:right eye pupil position z
        right_eye_sample[6]:right eye visual angle in spherical: theta
        right_eye_sample[7]:right eye visual angle in spherical: phi
        right_eye_sample[8]:right eye visual angle in vector: x
        right_eye_sample[9]:right eye visual angle in vector: y
        right_eye_sample[10]:right eye visual angle in vector: z
        right_eye_sample[11]:right eye pix per degree x
        right_eye_sample[12]:right eye pix per degree y
        right_eye_sample[13]:right eye valid (0:invalid 1:valid)
    """
    _gaze_right = [0, 0]
    _gaze_right[0] = data['right_eye_sample'][0] + random.randint(0, 30)
    _gaze_right[1] = data['right_eye_sample'][1] + random.randint(0, 30)

    _gaze_left = [0, 0]
    _gaze_left[0] = data['left_eye_sample'][0] + random.randint(0, 30)
    _gaze_left[1] = data['left_eye_sample'][1] + random.randint(0, 30)

    if random.random() < 0.02:
        my_filter.filter_sample(timestamp=data['timestamp'], left_gaze=[np.nan, np.nan], right_gaze=[np.nan, np.nan])
    elif random.random() < 0.04:
        my_filter.filter_sample(timestamp=data['timestamp'], left_gaze=_gaze_left, right_gaze=[np.nan, np.nan])
    elif random.random() < 0.06:
        my_filter.filter_sample(timestamp=data['timestamp'], left_gaze=[np.nan, np.nan], right_gaze=_gaze_right)
    else:
        my_filter.filter_sample(timestamp=data['timestamp'], left_gaze=_gaze_left, right_gaze=_gaze_right)


def subscribe_3(**kwargs):
    gaze_right[0] = kwargs['right_gaze'][0]
    gaze_right[1] = kwargs['right_gaze'][1]


deep_gaze.subscribe_sample(subscribe_1, subscribe_2)

# step 4: start eye tracking sampling
deep_gaze.start_sampling()

my_filter = Filter(2)
my_filter.subscribe(subscribe_3)

pygame.init()
# 获取显示器的宽度和高度
screen_info = pygame.display.Info()
screen_width = 1920
screen_height = 1080

# 设置全屏模式
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Display Mouse Position")

# 定义颜色
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# 定义圆圈的初始位置和半径
circle_radius = 20

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
    # 清屏
    screen.fill(WHITE)
    # 在鼠标位置画一个圆圈
    if gaze_right != np.nan:
        # filter_gaze_left, filter_gaze_right = my_filter.filter_sample(gaze_right, gaze_right)
        pygame.draw.circle(screen, RED, gaze_right, circle_radius)

    # 更新屏幕
    pygame.display.flip()

pygame.quit()

# step 5: show your task stimuli, you can send trigger when the stimulus shows via set_marker function.
deep_gaze.set_trigger(2)
time.sleep(4)
deep_gaze.set_trigger(4)
time.sleep(1)
# step 6: stop eye tracking sampling
deep_gaze.stop_sampling()

# step 7: save your eye tracking data
data_dir = "./data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

file_name = "example_data.csv"
deep_gaze.save_data(os.path.join(data_dir, file_name))
# The file format of save data is a .csv file.
# Its header includes timestamp, gaze_sample[0], gaze_sample[1], gaze_sample[2] ... gaze_sample[10], and marker (please
# see function 'subscribe_2').
deep_gaze.release()
