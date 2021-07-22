import json
import sys
import os

from csv_utils import CSV
# from vibration_utils import VibrationCSV

# keypoints = cu.CSV(filename="keypoint_csvs/test.csv", columns=)

def _get_columns():
	column_names = ['L-shoulder', 'R-shoulder',
		   'L-elbow', 'R-elbow',
		   'L-wrist', 'R-wrist']

	divisions = ['X', 'Y', 'Z']

	columns = []

	for column in column_names:
		for div in divisions:
			columns.append(f'{column}-{div}')

	columns.append('Timestamp')

	return columns

kpt_cols = _get_columns()

keypoint_csv = CSV(filename="keypoint_csvs/2_test.csv", columns=kpt_cols)
vibration_csv = CSV(filename="timestamp_csvs/2_test.csv", columns=['left', 'right'])

def on_connect(contents):
    print("Pose estimation camera connected")

def on_coords(contents):
    csv_list = json.loads(contents)
    keypoint_csv.add_list(csv_list)

def on_rcv_frame_count(contents):
    sys.stdout.write(f"\rCurrent frame number: {contents}")
    sys.stdout.flush()

def on_finish(contents):
    print(f"\n{contents}")

    keypoint_csv.filter_columns(window_length=5, polyorder=2,
                            columns=kpt_cols[:-1], overwrite=True)

    keypoint_csv.save()
    vibration_csv.save()

def on_vibration(contents):
    timestamp_list = json.loads(contents)
    vibration_csv.add_list(timestamp_list)
