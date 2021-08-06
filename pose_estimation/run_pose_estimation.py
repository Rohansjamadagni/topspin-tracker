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
parser.add_argument("--cam", type=int,
                    help="Camera number")

args = parser.parse_args()

args.lm_m = "831"
args.internal_fps = 25

def _get_list(landmarks):
    csv_list = []
    parts_list = ['left_shoulder', 'right_shoulder',
               'left_elbow', 'right_elbow',
               'left_wrist', 'right_wrist']

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

camera = args.cam

try:
    client.connect(broker_ip, broker_port)
except:
    exit()

client.publish(f'pose_{camera}/connected', json.dumps(f"Pose estimator {camera} connected!"))

def main():
    if camera == 1:
        frame_counter = 0

    while True:
        frame, body = pose.next_frame()

        if camera == 1 and frame_counter%60 == 0:
            client.publish(f'pose_{camera}/progress', json.dumps(frame_counter))

        frame_counter += 1

        if frame is None: break

        # Draw 2d skeleton
        frame = renderer.draw(frame, body)
        key = renderer.waitKey(delay=1)
        if key == 27 or key == ord('q'):
            break

        if body is not None:
            csv_list = _get_list(body.landmarks.tolist())
        else:
            csv_list = [[0 for _ in range(0, 19)]]

        client.publish(f'pose_{camera}/coords', json.dumps(csv_list))

        f = open('../flex.tape', 'r')
        number = int(f.read()[0])

        if number == 1:
            break

        f.close()

    client.publish(f'pose_{camera}/finished', json.dumps(f"Pose estimation camera {camera} has been terminated."))
    print(f"Pose camera {camera} finished")

    renderer.exit()
    pose.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        client.publish(f'pose_{camera}/error', json.dumps(e))
        exit()
