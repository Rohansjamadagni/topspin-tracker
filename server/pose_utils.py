import json
import sys
import os

import csv_utils as cu
import new_csv_utils as ncu
# from vibration_utils import VibrationCSV

# keypoints = cu.CSV(filename="keypoint_csvs/test.csv", columns=)

csv_file = f"keypoint_csvs/test.csv"
cu.initialize_csv(csv_file)

vibration_csv = CSV(filename="timestamp_csvs/test.csv", columns=['left', 'right'])

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
    vibration_csv.save()

def on_vibration(contents):
    timestamp_list = json.loads(contents)
    vibration_csv.add_list(timestamp_list)
