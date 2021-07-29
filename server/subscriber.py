import os
import subprocess
import json
import sys
import paho.mqtt.client as mqtt

from pose_utils import PoseCam
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

pose_1 = PoseCame(cam_number=1, csv_dest="keypoint_csvs/cam_1/test.csv")
pose_2 = PoseCame(cam_number=2, csv_dest="keypoint_csvs/cam_1/test.csv")

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

def on_connect_vib(client, userdata, detect_flags, rc):
    client.subscribe("vibration/#")
    print("Connected to the vibration topic!")
    print("Attempting to connect to sensors")

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
