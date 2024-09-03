import os
import random
import time

import pygame

from deepgaze import DeepGaze

pygame.init()
pygame.display.set_mode((1920, 1080))

deep_gaze = DeepGaze()
deep_gaze.create_session(session_name="example")

f = open('data/event.csv', 'w')
f.write('timestamp,left_velocity_cache,right_velocity_cache,left_acceleration_cache,right_acceleration_cache\n')
gaze_right = [0, 0]


def get_right_coordinate(data):
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
    gaze_right[0] = data['right_eye_sample'][0] + random.randint(0, 30)
    gaze_right[1] = data['right_eye_sample'][1] + random.randint(0, 30)


def oed_callback(**kwargs):
    # online event detection callback
    _timestamp = kwargs['timestamp'][-4]
    _l_v = kwargs['left_velocity_cache'][-4]
    _r_v = kwargs['right_velocity_cache'][-4]
    _l_a = kwargs['left_acceleration_cache'][-4]
    _r_a = kwargs['right_acceleration_cache'][-4]
    _l_g = kwargs['left_gaze_cache'][-4]
    _r_g = kwargs['right_gaze_cache'][-4]
    _l_ppd = kwargs['left_ppd_cache'][-4]
    _r_ppd = kwargs['right_ppd_cache'][-4]
    f.write(f'{_timestamp},{_l_v},{_r_v},{_l_g},{_r_g},{_l_ppd},{_r_ppd}\n')


deep_gaze.subscribe_sample(get_right_coordinate)  # deep_gaze.subscribe_sample(subscribe_2)
deep_gaze.subscribe_event(oed_callback)

# step 4: start eye tracking sampling
deep_gaze.start_sampling()

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
    pygame.draw.circle(screen, RED, gaze_right, circle_radius)

    # 更新屏幕
    pygame.display.flip()

pygame.quit()

deep_gaze.set_trigger(2)
time.sleep(4)
deep_gaze.set_trigger(4)
time.sleep(4)
# step 7: stop eye tracking sampling
deep_gaze.stop_sampling()

# step 8: save your eye tracking data
data_dir = "./data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

file_name = "example_data.csv"
deep_gaze.save_data(os.path.join(data_dir, file_name))
# The file format of save data is a .csv file.
# Its header includes timestamp, gaze_sample[0], gaze_sample[1], gaze_sample[2] ... gaze_sample[10], and marker (please
# see function 'subscribe_2').
deep_gaze.release()
f.close()
