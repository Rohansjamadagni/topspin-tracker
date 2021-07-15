#!/usr/bin/env python3

import subprocess
import signal
import argparse
import time
import json

import paho.mqtt.client as mqtt

from BlazeposeRenderer import BlazeposeRenderer
from BlazeposeDepthaiEdge import BlazeposeDepthai

from mediapipe_utils import KEYPOINT_DICT

parser = argparse.ArgumentParser()

parser.add_argument('-i', '--input', type=str, default="rgb",
                    help="'rgb' or 'rgb_laconic' or path to video/image file to use as input (default=%(default)s)")
parser.add_argument("--pd_m", type=str,
                    help="Path to an .blob file for pose detection model")
parser.add_argument("--lm_m", type=str,
                    help="Landmark model ('full' or 'lite' or '831') or path to an .blob file (default=%(default)s)")
parser.add_argument('-c', '--crop', action="store_true",
                    help="Center crop frames to a square shape before feeding pose detection model")
parser.add_argument('--no_smoothing', action="store_true",
                    help="Disable smoothing filter")
parser.add_argument('--filter_window_size', type=int, default=5,
                    help="Smoothing filter window size. Higher value adds to lag and to stability (default=%(default)i)")
parser.add_argument('--filter_velocity_scale', type=float, default=10,
                    help="Smoothing filter velocity scale. Lower value adds to lag and to stability (default=%(default)s)")
parser.add_argument('-f', '--internal_fps', type=int,
                    help="Fps of internal color camera. Too high value lower NN fps (default= depends on the model)")
parser.add_argument('--internal_frame_height', type=int, default=640,
                    help="Internal color camera frame height in pixels (default=%(default)i)")
parser.add_argument('-s', '--stats', action="store_true",
                    help="Print some statistics at exit")
parser.add_argument('-t', '--trace', action="store_true",
                    help="Print some debug messages")
parser.add_argument('--force_detection', action="store_true",
                    help="Force person detection on every frame (never use landmarks from previous frame to determine ROI)")
parser.add_argument('-3', '--show_3d', action="store_true",
                    help="Display skeleton in 3d in a separate window (valid only for full body landmark model)")
parser.add_argument("-o","--output",
                    help="Path to output video file")
parser.add_argument("-co","--csv-output",
                    help="Path to output csv file")

args = parser.parse_args()

def _get_list(landmarks):
    csv_list = []
    parts_list = ['nose',
               'left_eye', 'right_eye',
               'left_ear', 'right_ear',
               'left_shoulder', 'right_shoulder',
               'left_elbow', 'right_elbow',
               'left_wrist', 'right_wrist',
               'left_hip', 'right_hip',
               'left_knee', 'right_knee',
               'left_ankle', 'right_ankle']

    for part in parts_list:
        coords = landmarks[KEYPOINT_DICT[part]]
        csv_list.extend([coords[0], coords[1], coords[2]])

    csv_list.append(time.time())

    return [csv_list]

pose = BlazeposeDepthai(input_src=args.input,
            pd_model=args.pd_m,
            lm_model=args.lm_m,
            smoothing=not args.no_smoothing,
            filter_window_size=args.filter_window_size,
            filter_velocity_scale=args.filter_velocity_scale,
            crop=args.crop,
            internal_fps=args.internal_fps,
            internal_frame_height=args.internal_frame_height,
            force_detection=args.force_detection,
            stats=args.stats,
            trace=args.trace)

renderer = BlazeposeRenderer(
                pose,
                show_3d=args.show_3d,
                output=f"videos/{args.output}")

broker_config = json.load(open('../ips.json', 'r'))
broker_ip = broker_config['broker_ip']
broker_port = broker_config['broker_port']

client = mqtt.Client()

try:
    client.connect(broker_ip, broker_port)
except:
    exit()

client.publish('pose/connected', json.dumps("Pose estimator connected!"))

vib_process = subprocess.Popen(["python3", "vibrator.py"])

def main():
    frame_counter = 0

    while True:
        frame, body = pose.next_frame()

        prev_list = None

        client.publish('pose/progress', json.dumps(frame_counter+1))
        frame_counter += 1

        if frame is None: break

        # Draw 2d skeleton
        frame = renderer.draw(frame, body)
        key = renderer.waitKey(delay=1)
        if key == 27 or key == ord('q'):
            break

        if body is not None:
            csv_list = _get_list(body.landmarks.tolist())
            prev_list = csv_list
        elif prev_list is not None:
            csv_list = prev_list
        else:
            continue

        client.publish('pose/coords', json.dumps(csv_list))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        renderer.exit()
        pose.exit()

        client.publish('pose/finished', json.dumps("Pose estimation camera has been terminated."))
        # subprocess.Popen(["pkill", "-INT", "-f", "vibrator.py"])
        vib_process.send_signal(signal.SIGINT)

        exit()
