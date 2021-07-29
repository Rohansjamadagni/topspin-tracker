import os
import subprocess
import json
import sys
import paho.mqtt.client as mqtt

import pose_utils as pu
import ball_utils as bu
import ansible_utils as au
import vibration_utils as vu

from csv_utils import CSV

broker_config = json.load(open('../ips.json', 'r'))
broker_ip = broker_config['broker_ip']
broker_port = broker_config['broker_port']

keypoint_csv_1 = CSV(filename="keypoint_csvs/cam_1/test.csv", columns=pu._get_columns())
keypoint_csv_2 = CSV(filename="keypoint_csvs/cam_2/test.csv", columns=pu._get_columns())

vib = mqtt.Client()
ball = mqtt.Client()
pose_1 = mqtt.Client()
pose_2 = mqtt.Client()

vib.connect(broker_ip, broker_port)
ball.connect(broker_ip, broker_port)
pose_1.connect(broker_ip, broker_port)
pose_2.connect(broker_ip, broker_port)

def pack(error=None):
    if error is not None:
        print(error)
    print("PACK BRO")
    au.ansible_destroy()
    exit()

def on_connect_ball(client, userdata, detect_flags, rc):
    client.subscribe("ball/#")
    print("Connected to the ball topic!")
    print("Attempting to connect to ball camera")

def on_connect_pose_1(client, userdata, detect_flags, rc):
    client.subscribe("pose_1/#")
    print("Connected to the pose_1 topic!")
    print("Attempting to connect to pose_1 camera")
    # au.ansible()

def on_connect_pose_2(client, userdata, detect_flags, rc):
    client.subscribe("pose_2/#")
    print("Connected to the pose_2 topic!")
    print("Attempting to connect to pose_2 camera")
    # au.ansible()

def on_connect_vib(client, userdata, detect_flags, rc):
    client.subscribe("vibration/#")
    print("Connected to the vibration topic!")
    print("Attempting to connect to sensors")

def on_message_pose_1(client, ud, msg):
    contents = msg.payload.decode()

    if msg.topic == 'pose_1/connected':
        pu.on_connect(contents)
    elif msg.topic == 'pose_1/coords':
        pu.on_coords(contents)
    elif msg.topic == 'pose_1/progress':
        pu.on_rcv_frame_count(contents)
    elif msg.topic == 'pose_1/vibration':
        pu.on_vibration(contents)
    elif msg.topic == 'pose_1/finished':
        pu.on_finish(contents)
    elif msg.topic == 'pose_1/error':
        pack(contents)
    else:
        print('Wrong pose_1 topic')

def on_message_pose_2(client, ud, msg):
    contents = msg.payload.decode()

    if msg.topic == 'pose_2/connected':
        pu.on_connect(contents)
    elif msg.topic == 'pose_2/coords':
        pu.on_coords(contents)
    elif msg.topic == 'pose_2/finished':
        pu.on_finish(contents)
    elif msg.topic == 'pose_2/error':
        pack(contents)
    else:
        print('Wrong pose_2 topic')

def on_message_vib(client, ud, msg):
    contents = msg.payload.decode()

    if msg.topic == 'vibration/connected':
        vu.on_connect(contents)
    elif msg.topic == 'vibration/pitch':
        vu.on_vibration(contents)
    elif msg.topic == 'vibration/finished':
        vu.on_finish(contents)
    elif msg.topic == 'vibration/error':
        pack(contents)
    else:
        print('Wrong pose_1 topic')

def on_message_ball(client, ud, msg):
    contents = msg.payload.decode()

    if msg.topic == 'ball/connected':
        bu.on_connect(contents)
    elif msg.topic == 'ball/progress/record':
        bu.on_record(contents)
    elif msg.topic == 'ball/record/finished':
        bu.on_finish_record(contents)
    elif msg.topic == 'ball/progress/replay':
        bu.on_replay(contents)
    # receive data from ansible to start replay
    elif msg.topic == 'ball/replay/finished':
        bu.on_finish_replay(contents)
    elif msg.topic == 'ball/error':
        pack(contents)
    else:
        print('Wrong ball topic')

while True:
    # ball.on_connect = on_connect_ball
    # ball.on_message = on_message_ball
    try:
        vib.on_connect = on_connect_vib
        vib.on_message = on_message_vib

        pose_1.on_connect = on_connect_pose_1
        pose_1.on_message = on_message_pose_1

        pose_2.on_connect = on_connect_pose_2
        pose_2.on_message = on_message_pose_2

        # ball.loop_start()
        vib.loop_start()
        pose_1.loop_start()
        pose_2.loop_start()
    except KeyboardInterrupt:
        # print("Press r top stop recording, Press q to quit:")
        # inp = input()
        # if(inp == 'r'):
        #     au.stat_replay()
        # else:
        exit()
