import json
import sys
import os

import csv_utils as cu
from vibration_utils import VibrationCSV

csv_file = f"keypoint_csvs/test.csv"
cu.initialize_csv(csv_file)

vibration_csv = VibrationCSV(filename="timestamp_csvs/test.csv")

def on_connect(contents):
    print("Pose estimation camera connected")

def on_coords(contents):
    csv_list = json.loads(contents)
    cu.write_list_to_csv(csv_file, csv_list)

def on_rcv_frame_count(contents):
    sys.stdout.write(f"\rCurrent frame number: {contents}")
    sys.stdout.flush()

def on_finish(contents):
    print(f"\n{contents}")
    cu.filter_file(csv_file, hand="right",
                window_length=5, polyorder=2)

def on_vibration(contents):
    timestamp_list = json.loads(content)
    vibration_csv.write_list_to_csv(timestamp_list)
