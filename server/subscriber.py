# subscriber
import paho.mqtt.client as mqtt
import os
import subprocess
import pose_utils as pu
import ball_utils as bu
import ansible_utils as au

broker_ip = json.load(open('../config.json', 'r'))['broker']

ball = mqtt.Client()
pose = mqtt.Client()

ball.connect(broker_ip, 1883)
pose.connect(broker_ip, 1883)

def on_failure():
    print("PACKED AF")
    au.ansible_destroy()
    sys.exit(1)

def on_connect_ball(client, userdata, detect_flags, rc):
    client.subscribe("ball/#")
    print("Connected to the ball topic!")
    print("Attempting to connect to ball camera")
    au.ansible()

def on_connect_pose(client, userdata, detect_flags, rc):
    client.subscribe("pose/#")
    print("Connected to the pose topic!")
    print("Attempting to connect to pose camera")
    au.ansible()

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
    else:
        print('Wrong pose topic')

def on_message_ball(client, ud, msg):
    contents = msg.payload.decode()

    if msg.topic == 'ball/connected':
        bu.on_connect(contents)
    elif msg.topic == 'ball/progress/record':
        bu.on_record(contents)
    elif msg.topic == 'ball/progress/replay':
        bu.on_replay(contents)
    # receive data from ansible to start replay
    else:
        print('Wrong ball topic')

while True:
    ball.on_connect = on_connect_ball
    ball.on_message = on_message_ball

    pose.on_connect = on_connect_pose
    pose.on_message = on_message_pose

    ball.loop_start()
    pose.loop_start()
