# subscriber
import paho.mqtt.client as mqtt
import os
from multiprocessing.pool import ThreadPool

client = mqtt.Client()
client.connect('10.147.17.95', 1883)
detect_flag = [False,False]
recorded_flag =[False,False]

def on_connect(client, userdata, detect_flags, rc):
    client.subscribe("topspin/test")
    print("Connected to a broker!")
    print("Attempting to connect to cameras")
    ansible()

def ansible():
    os.system('ansible-playbook -i ../ansible/hosts ../ansible/scrpit.yml --tags "mqtt_connect" &')

def start_record():
    os.system('ansible-playbook -i ../ansible/hosts ../ansible/scrpit.yml --tags "start_record" &')

def start_replay():
    os.system('ansible-playbook -i ../ansible/hosts ../ansible/scrpit.yml --tags "start_replay" &')


def on_message(client, userdata, message):
    if(message.payload.decode() == "Ball Detector Connected"):
        print("Ball detector connected")
        detect_flag[0] = True
    if(message.payload.decode() == "Pose Estimator Connected"):
        print("Pose Estimator connected")
        detect_flag[1] = True
    if detect_flag[0] and detect_flag[1]:
        detect_flag[0] = False
        start_start_pose_recording record()
    if(message.payload.decode() == "Ball Detector Done"):
        print("Ball Detector Done")
        recorded_flag[0] = True
    if(message.payload.decode() == "Pose Estimator Done"):
        print("Pose Estimator Done")
        recorded_flag[1] = True
    if recorded_flag[0] and recorded_flag[1]:
        recorded_flag[0] = False
        start_replay()

    print(message.payload.decode())

while True:
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_start()