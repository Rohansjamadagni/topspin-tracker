import os
import subprocess
import json
import sys

from server_utils import PoseCam, BallCam, Vibrator, Ansible

broker_config = json.load(open('../ips.json', 'r'))
broker_ip = broker_config['broker_ip']
broker_port = broker_config['broker_port']

vib = Vibrator(cam_number=1, csv_dest="timestamp_csvs/test.csv")
ball = BallCam(cam_number=1)
pose_1 = PoseCam(cam_number=1, csv_dest="keypoint_csvs/cam_1/test.csv")
pose_2 = PoseCam(cam_number=2, csv_dest="keypoint_csvs/cam_2/test.csv")

vib.connect(broker_ip, broker_port)
ball.connect(broker_ip, broker_port)

pose_1.connect(broker_ip, broker_port)
pose_2.connect(broker_ip, broker_port)

while True:
    try:
        # ball.loop_start()
        vib.loop_start()

        pose_1.loop_start()
        pose_2.loop_start()
    except KeyboardInterrupt:
        print('s to stop recording and q to quit')
        input_ = input()
        if input_ == 'q':
            ball.destroy()
            exit()
        if input_ == 's':
            ball.destroy()
