import json
import sys
import os

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

def on_connect(contents):
    print(contents)

def on_coords(contents, csv_obj):
    csv_list = json.loads(contents)
    csv_obj.add_list(csv_list)

def on_rcv_frame_count(contents):
    sys.stdout.write(f"\rCurrent frame number: {contents}")
    sys.stdout.flush()

def on_finish(contents, csv_obj):
    print(f"\n{contents}")

    csv_obj.filter_columns(window_length=5, polyorder=2,
                            columns=kpt_cols[:-1], overwrite=True)

    csv_obj.save()
