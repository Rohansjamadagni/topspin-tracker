# subscriber
import paho.mqtt.client as mqtt
import os
import pose_utils
import ball_utils

ball = mqtt.Client()
pose = mqtt.Client()

ball.connect('10.147.17.95', 1883)
pose.connect('10.147.17.95', 1883)

def on_connect_ball(client, userdata, detect_flags, rc):
    client.subscribe("ball/#")
    print("Connected to the ball topic!")
    print("Attempting to connect to ball camera")
    ansible()

def on_connect_pose(client, userdata, detect_flags, rc):
    client.subscribe("pose/#")
    print("Connected to the pose topic!")
    print("Attempting to connect to pose camera")
    ansible()

def ansible():
    os.system('ansible-playbook -i ../ansible/hosts ../ansible/control.yml --tags "mqtt_connect" &')

def start_record():
    os.system('ansible-playbook -i ../ansible/hosts ../ansible/control.yml --tags "start_record" &')

def start_replay():
    os.system('ansible-playbook -i ../ansible/hosts ../ansible/control.yml --tags "start_replay" &')

def on_message_pose(client, ud, msg):
    contents = msg.payload.decode()

    if msg.topic == 'pose/connected':
        pose_utils.on_connect(contents)
    elif msg.topic == 'pose/coords':
        pose_utils.on_coords(contents)
    elif msg.topic == 'pose/progress':
        pose_utils.on_rcv_frame_count(contents)
    elif msg.topic == 'pose/vibration':
        pose_utils.on_vibration(contents)
    else:
        print('Wrong pose topic')

def on_message_ball(client, ud, msg):
    contents = msg.payload.decode()

    if msg.topic == 'ball/connected':
        ball_utils.on_connect(contents)
    elif msg.topic == 'ball/progress/record':
        ball_utils.on_record(contents)
    elif msg.topic == 'ball/progress/replay':
        ball_utils.on_replay(contents)
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
