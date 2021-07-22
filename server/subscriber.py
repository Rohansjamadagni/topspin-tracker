import os
import subprocess
import json
import sys
import paho.mqtt.client as mqtt

import pose_utils as pu
import ball_utils as bu
import ansible_utils as au

broker_config = json.load(open('../ips.json', 'r'))
broker_ip = broker_config['broker_ip']
broker_port = broker_config['broker_port']

ball = mqtt.Client()
pose = mqtt.Client()

ball.connect(broker_ip, broker_port)
pose.connect(broker_ip, broker_port)

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

def on_connect_pose(client, userdata, detect_flags, rc):
    client.subscribe("pose/#")
    print("Connected to the pose topic!")
    print("Attempting to connect to pose camera")
    # au.ansible()

def on_message_pose(client, ud, msg):
    contents = msg.payload.decode()

    if msg.topic == 'pose/connected':
        pu.on_connect(contents)
    elif msg.topic == 'pose/coords':
        pu.on_coords(contents)
    elif msg.topic == 'pose/progress':
        pu.on_rcv_frame_count(contents)
    elif msg.topic == 'pose/vibration':
        pu.on_vibration(contents)
    elif msg.topic == 'pose/finished':
        pu.on_finish(contents)
    elif msg.topic == 'pose/error':
        pack(contents)
    else:
        print('Wrong pose topic')

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
        pose.on_connect = on_connect_pose
        pose.on_message = on_message_pose

        # ball.loop_start()
        pose.loop_start()
    except KeyboardInterrupt:
        # print("Press r top stop recording, Press q to quit:")
        # inp = input()
        # if(inp == 'r'):
        #     au.stat_replay()
        # else:
        exit()
