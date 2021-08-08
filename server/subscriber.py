import os
import subprocess
import json
import sys

import argparse

# parser = argparse.ArgumentParser()

# parser.add_argument("-c","--csv",
#                     help="Path to output csv file from cams")

# args = parser.parse_args()

from server_utils import PoseCam, BallCam, Vibrator, Ansible

broker_config = json.load(open('../ips.json', 'r'))
broker_ip = broker_config['broker_ip']
broker_port = broker_config['broker_port']

vib = Vibrator(cam_number=1, csv_dest=f"timestamp_csvs/result.csv")
ball = BallCam(cam_number=1)
pose_1 = PoseCam(cam_number=1, csv_dest=f"keypoint_csvs/cam_1/result.csv")
pose_2 = PoseCam(cam_number=2, csv_dest=f"keypoint_csvs/cam_2/result.csv")

vib.connect(broker_ip, broker_port)
ball.connect(broker_ip, broker_port)

pose_1.connect(broker_ip, broker_port)
pose_2.connect(broker_ip, broker_port)

while True:
    try:
        ball.loop_start()
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
