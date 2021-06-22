import argparse
import threading
import time
from pathlib import Path
from pose_utils import getKeypoints, getValidPairs, getPersonwiseKeypoints
import cv2
import depthai as dai
import numpy as np
from imutils.video import FPS
import os
import csv_utils as cu

globals = {'h': None, 'w': None,
		   'running': True,
		   'keypoints_list': None,
		   'detected_keypoints': None,
		   'personwiseKeypoints': None}

parser = argparse.ArgumentParser()

parser.add_argument('-co', '--csv_output', help="Enter where to save the csv file along with file name",default='result.csv')
parser.add_argument('-i', '--input', help="Enter path to directory obtained from record.py",default='data/')

args = parser.parse_args()

assert args.csv_output is not None
assert args.input is not None


def _get_list(detected_keypoints: list) -> list:

	csv_list = []
	for pt in detected_keypoints:
		if len(pt) != 0:
			pt_list = []
			pt_list += [
				pt[0][0], pt[0][1], pt[0][2]
			]
			csv_list.extend(pt_list)
		else:
			csv_list.extend([0, 0, 0])

	return [csv_list]


def to_planar(arr: np.ndarray, shape: tuple) -> list:
	return cv2.resize(arr, shape).transpose(2,0,1).flatten()

def create_pipeline():

	print("Creating pipeline...")
	pipeline = dai.Pipeline()

	# NeuralNetwork
	print("Creating Human Pose Estimation Neural Network...")
	pose_nn = pipeline.createNeuralNetwork()

	pose_nn.setBlobPath(str(Path("models/pose.blob").resolve().absolute()))
	# Increase threads for detection
	pose_nn.setNumInferenceThreads(2)
	# Specify that network takes latest arriving frame in non-blocking manner
	pose_nn.input.setQueueSize(1)
	pose_nn.input.setBlocking(False)
	pose_nn_xout = pipeline.createXLinkOut()
	pose_nn_xout.setStreamName("pose_nn")
	pose_nn.out.link(pose_nn_xout.input)

	pose_in = pipeline.createXLinkIn()
	pose_in.setStreamName("pose_in")
	pose_in.out.link(pose_nn.input)

	print("Pipeline created.")
	return pipeline


colors = [[0, 100, 255], [0, 100, 255], [0, 255, 255], [0, 100, 255], [0, 255, 255], [0, 100, 255], [0, 255, 0],
		  [255, 200, 100], [255, 0, 255], [0, 255, 0], [255, 200, 100], [255, 0, 255], [0, 0, 255], [255, 0, 0],
		  [200, 200, 0], [255, 0, 0], [200, 200, 0], [0, 0, 0]]
POSE_PAIRS = [[1, 2], [1, 5], [2, 3], [3, 4], [5, 6], [6, 7], [1, 8], [8, 9], [9, 10], [1, 11], [11, 12], [12, 13],
			  [1, 0], [0, 14], [14, 16], [0, 15], [15, 17], [2, 17], [5, 16]]

def pose_thread(in_queue):
	global globals

	while globals['running']:
		try:
			raw_in = in_queue.get()
		except RuntimeError:
			return

		heatmaps = np.array(raw_in.getLayerFp16('Mconv7_stage2_L2')).reshape((1, 19, 32, 57))
		pafs = np.array(raw_in.getLayerFp16('Mconv7_stage2_L1')).reshape((1, 38, 32, 57))
		heatmaps = heatmaps.astype('float32')
		pafs = pafs.astype('float32')
		outputs = np.concatenate((heatmaps, pafs), axis=1)

		new_keypoints = []
		new_keypoints_list = np.zeros((0, 3))
		keypoint_id = 0

		for row in range(18):
			probMap = outputs[0, row, :, :]
			probMap = cv2.resize(probMap, (globals['w'], globals['h']))  # (456, 256)
			keypoints = getKeypoints(probMap, 0.2)
			new_keypoints_list = np.vstack([new_keypoints_list, *keypoints])
			keypoints_with_id = []

			for i in range(len(keypoints)):
				keypoints_with_id.append(keypoints[i] + (keypoint_id,))
				keypoint_id += 1

			new_keypoints.append(keypoints_with_id)

		valid_pairs, invalid_pairs = getValidPairs(outputs, globals['w'], globals['h'], new_keypoints)
		newPersonwiseKeypoints = getPersonwiseKeypoints(valid_pairs, invalid_pairs, new_keypoints_list)

		globals['detected_keypoints'], globals['keypoints_list'], globals['personwiseKeypoints'] = (new_keypoints, new_keypoints_list, newPersonwiseKeypoints)


def main():
	global globals

	valid_frames = os.listdir(args.input)
	frames = sorted([int(i) for i in valid_frames])

	with dai.Device(create_pipeline()) as device:
		print("Starting pipeline...")
		device.startPipeline()

		cu.initialize_csv(args.csv_output, dataset="oak-d-coco")

		pose_in = device.getInputQueue("pose_in")
		pose_nn = device.getOutputQueue("pose_nn", 1, False)
		t = threading.Thread(target=pose_thread, args=(pose_nn, ))
		t.start()

		# print('Warmup...')
		# time.sleep(2)

		num_skipped_frames = None

		print('Running...')

		for frame in frames:
			image = cv2.imread(f'{args.input}/{frame}/color.jpeg')

			if image is None:
				break

			globals['h'], globals['w'] = image.shape[:2]

			nn_data = dai.NNData()
			nn_data.setLayer("input", to_planar(image, (456, 256)))
			pose_in.send(nn_data)

			if globals['detected_keypoints'] is not None:
				if num_skipped_frames is None:
					num_skipped_frames = frame

				csv_list = _get_list(globals['detected_keypoints'])
				cu.write_list_to_csv(args.csv_output, csv_list, dataset="oak-d-coco")

		print('Processing skipped frames...')

		for frame in range(0, num_skipped_frames):
			image = cv2.imread(f'{args.input}/{frame}/color.jpeg')

			if image is None:
				break

			globals['h'], globals['w'] = image.shape[:2]

			nn_data = dai.NNData()
			nn_data.setLayer("input", to_planar(image, (456, 256)))
			pose_in.send(nn_data)

			if globals['detected_keypoints'] is not None:
				csv_list = _get_list(globals['detected_keypoints'])
				cu.write_list_to_csv(args.csv_output, csv_list, dataset="oak-d-coco", beginning=True)

		print('CSV file done. Filtering...')

		cu._filter_file(args.csv_output, hand="left", window_length=13, polyorder=2)

		print('Done.')

if __name__ == "__main__":
	main()
