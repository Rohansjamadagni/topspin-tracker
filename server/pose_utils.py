import csv_utils as cu
import json
import sys

csv_file = "csvs/test.csv"

def on_connect(contents):
    print("Pose estimation camera connected")

def on_coords(contents):
    csv_list = json.loads(contents)
    cu.write_list_to_csv(csv_file, csv_list, dataset="coco")

def on_rcv_frame_count(contents):
    sys.stdout.write(f"\rCurrent frame number: {contents}")
    sys.stdout.flush()

def on_vibration(contents):
    pass
