import os
import random
import time
import numpy as np
import pygame
from deepgaze import DeepGaze
from deepgaze.event_detection import OnlineEventDetection
from deepgaze.filter import Filter

deep_gaze = DeepGaze()
deep_gaze.create_session(session_name="example")

oed = OnlineEventDetection()

f = open('data/event.csv', 'w')
f.write('timestamp,left_velocity_cache,right_velocity_cache,left_acceleration_cache,right_acceleration_cache\n')


def subscribe_2(data):
    data['right_eye_sample'][0] += random.randint(0, 30)
    data['right_eye_sample'][1] += random.randint(0, 30)

    data['left_eye_sample'][0] += random.randint(0, 30)
    data['left_eye_sample'][1] += random.randint(0, 30)


def oed_callback(**kwargs):
    _timestamp = kwargs['timestamp'][-4]

    _l_v = kwargs['left_velocity_cache'][-4]
    _r_v = kwargs['right_velocity_cache'][-4]
    _l_a = kwargs['left_acceleration_cache'][-4]
    _r_a = kwargs['right_acceleration_cache'][-4]
    f.write(f'{_timestamp},{_l_v},{_r_v},{_l_a},{_r_a}\n')


deep_gaze.subscribe_sample(subscribe_2, oed.handle_sample)
# deep_gaze.subscribe_sample(subscribe_2)
oed.subscribe(oed_callback)

# step 4: start eye tracking sampling
deep_gaze.start_sampling()

# step 5: show your task stimuli, you can send trigger when the stimulus shows via set_marker function.
deep_gaze.set_trigger(2)
time.sleep(4)
deep_gaze.set_trigger(4)
time.sleep(6)
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
f.close()
