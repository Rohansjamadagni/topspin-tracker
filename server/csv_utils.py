import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
import os
import cv2

# MPII : (0 - r ankle, 1 - r knee, 2 - r hip, 3 - l hip, 4 - l knee, 5 - l ankle, 6 - pelvis,
# 7 - thorax, 8 - upper neck, 9 - head top, 10 - r wrist, 11 - r elbow, 12 - r shoulder, 13 - l shoulder, 14 - l elbow, 15 - l wrist)

def _get_columns():
	column_names = ['Nose',
		   'L-eye', 'R-eye',
		   'L-ear', 'R-ear',
		   'L-shoulder', 'R-shoulder',
		   'L-elbow', 'R-elbow',
		   'L-wrist', 'R-wrist',
		   'L-hip', 'R-hip',
		   'L-knee', 'R-knee',
		   'L-ankle', 'R-ankle']

	divisions = ['X', 'Y', 'Z']

	columns = []

	for column in column_names:
		for div in divisions:
			columns.append(f'{column}-{div}')

	columns.append('Timestamp')

	return columns

def initialize_csv(filename):
	columns = _get_columns()

	df = pd.DataFrame(columns=columns)
	df.to_csv(f'{filename}')

	# releasing memory
	del df

def write_list_to_csv(filename, list, beginning=False):
	columns = _get_columns()
	# print(columns)

	if beginning:
		existing_df = pd.read_csv(f'{filename}', names=columns)
		new_row = pd.DataFrame(list, columns=columns)
		# print("new row: ", len(new_row.iloc[0, :]))
		# print("existing: ", len(existing_df.iloc[0, :]))
		df = pd.concat([new_row, existing_df.iloc[1:, :]]).reset_index(drop = True)
		df.to_csv(f'{filename}', mode='w', header=True)
	else:
		df = pd.DataFrame(list, columns=columns)
		df.to_csv(f'{filename}', mode='a', header=False)

def filter_file(csv_file, hand, window_length, polyorder):
	df = pd.read_csv(csv_file, delimiter=',')

	if hand == 'right':
		wrist_x = np.array(df['R-wrist-X'])
		wrist_y = np.array(df['R-wrist-Y'])
		elbow_x = np.array(df['R-elbow-X'])
		elbow_y = np.array(df['R-elbow-Y'])
		r_shoulder_x = np.array(df['R-shoulder-X'])
		r_shoulder_y = np.array(df['R-shoulder-Y'])
		l_shoulder_x = np.array(df['L-shoulder-X'])
		l_shoulder_y = np.array(df['L-shoulder-Y'])

		wrist_x_filtered = savgol_filter(wrist_x, window_length, polyorder, mode='nearest')
		wrist_y_filtered = savgol_filter(wrist_y, window_length, polyorder, mode='nearest')
		elbow_x_filtered = savgol_filter(elbow_x, window_length, polyorder, mode='nearest')
		elbow_y_filtered = savgol_filter(elbow_y, window_length, polyorder, mode='nearest')
		r_shoulder_x_filtered = savgol_filter(r_shoulder_x, window_length, polyorder, mode='nearest')
		r_shoulder_y_filtered = savgol_filter(r_shoulder_y, window_length, polyorder, mode='nearest')
		l_shoulder_x_filtered = savgol_filter(l_shoulder_x, window_length, polyorder, mode='nearest')
		l_shoulder_y_filtered = savgol_filter(l_shoulder_y, window_length, polyorder, mode='nearest')

		df['R-wrist-X-Filtered'] = wrist_x_filtered
		df['R-wrist-Y-Filtered'] = wrist_y_filtered
		df['R-elbow-X-Filtered'] = elbow_x_filtered
		df['R-elbow-Y-Filtered'] = elbow_y_filtered
		df['R-shoulder-X-Filtered'] = r_shoulder_x_filtered
		df['R-shoulder-Y-Filtered'] = r_shoulder_y_filtered
		df['L-shoulder-X-Filtered'] = l_shoulder_x_filtered
		df['L-shoulder-Y-Filtered'] = l_shoulder_y_filtered

		df.to_csv(csv_file, index=False)

	elif hand == 'left':
		wrist_x = np.array(df['L-wrist-X'])
		wrist_y = np.array(df['L-wrist-Y'])
		elbow_x = np.array(df['L-elbow-X'])
		elbow_y = np.array(df['L-elbow-Y'])
		r_shoulder_x = np.array(df['L-shoulder-X'])
		r_shoulder_y = np.array(df['L-shoulder-Y'])
		l_shoulder_x = np.array(df['R-shoulder-X'])
		l_shoulder_y = np.array(df['R-shoulder-Y'])

		wrist_x_filtered = savgol_filter(1280 - wrist_x, window_length, polyorder, mode='nearest')
		wrist_y_filtered = savgol_filter(wrist_y, window_length, polyorder, mode='nearest')
		elbow_x_filtered = savgol_filter(1280 - elbow_x, window_length, polyorder, mode='nearest')
		elbow_y_filtered = savgol_filter(elbow_y, window_length, polyorder, mode='nearest')
		r_shoulder_x_filtered = savgol_filter(1280 - r_shoulder_x, window_length, polyorder, mode='nearest')
		r_shoulder_y_filtered = savgol_filter(r_shoulder_y, window_length, polyorder, mode='nearest')
		l_shoulder_x_filtered = savgol_filter(1280 - l_shoulder_x, window_length, polyorder, mode='nearest')
		l_shoulder_y_filtered = savgol_filter(l_shoulder_y, window_length, polyorder, mode='nearest')

		df['R-wrist-X-Filtered'] = wrist_x_filtered
		df['R-wrist-Y-Filtered'] = wrist_y_filtered
		df['R-elbow-X-Filtered'] = elbow_x_filtered
		df['R-elbow-Y-Filtered'] = elbow_y_filtered
		df['R-shoulder-X-Filtered'] = r_shoulder_x_filtered
		df['R-shoulder-Y-Filtered'] = r_shoulder_y_filtered
		df['L-shoulder-X-Filtered'] = l_shoulder_x_filtered
		df['L-shoulder-Y-Filtered'] = l_shoulder_y_filtered

		df.to_csv(csv_file, index=False)

def normalize_file(csv_file, vid):
	df = pd.read_csv(csv_file, delimiter=',', engine='python')

	cap = cv2.VideoCapture(vid)

	ret, frame = cap.read()
	shape = frame.shape
	cap.release()
	cv2.destroyAllWindows

	wrist_x_filtered = np.array(df['R-wrist-X-Filtered'])
	wrist_y_filtered = np.array(df['R-wrist-Y-Filtered'])
	elbow_x_filtered = np.array(df['R-elbow-X-Filtered'])
	elbow_y_filtered = np.array(df['R-elbow-Y-Filtered'])
	r_shoulder_x_filtered = np.array(df['R-shoulder-X-Filtered'])
	r_shoulder_y_filtered = np.array(df['R-shoulder-Y-Filtered'])
	l_shoulder_x_filtered = np.array(df['L-shoulder-X-Filtered'])
	l_shoulder_y_filtered = np.array(df['L-shoulder-Y-Filtered'])

	h, w, c = shape

	wrist_x_normalized = wrist_x_filtered/w
	wrist_y_normalized = wrist_y_filtered/h
	elbow_x_normalized = elbow_x_filtered/w
	elbow_y_normalized = elbow_y_filtered/h
	r_shoulder_x_normalized = r_shoulder_x_filtered/w
	r_shoulder_y_normalized = r_shoulder_y_filtered/h
	l_shoulder_x_normalized = l_shoulder_x_filtered/w
	l_shoulder_y_normalized = l_shoulder_y_filtered/h

	df['R-wrist-X-Norm'] = wrist_x_normalized
	df['R-wrist-Y-Norm'] = wrist_y_normalized
	df['R-elbow-X-Norm'] = elbow_x_normalized
	df['R-elbow-Y-Norm'] = elbow_y_normalized
	df['R-shoulder-X-Norm'] = r_shoulder_x_normalized
	df['R-shoulder-Y-Norm'] = r_shoulder_y_normalized
	df['L-shoulder-X-Norm'] = l_shoulder_x_normalized
	df['L-shoulder-Y-Norm'] = l_shoulder_y_normalized

	df.to_csv(csv_file, index=False)

def csv_savgol_filter_directory(csv_dir, hand, window_length=13, polyorder=2):
	for csv_file in os.listdir(csv_dir):
		filter_file(os.path.join(csv_dir, csv_file), hand, window_length, polyorder)
