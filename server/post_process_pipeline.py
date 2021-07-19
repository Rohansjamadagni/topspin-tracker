import os

import sys
sys.path.insert(0, '..')
from pose_estimation.data_preparation.utils import DataSplitter

def pose_process(all_strokes):
    '''
    1. send batch of strokes for inference
    2. gather all labels into some global var and then send it to the web UI
    '''
    pass

def ball_process(all_rallies):
    '''
    1. run ansible start_replay (?)
    2. send rally splits to the camera for replay (?)
    3. gather all inferences like pos, speed and trajectory into some global vars and
       then send it to the web UI
    '''
    pass

def main():
    pose_splitter = DataSplitter(
        full_keypoint_file="keypoint_csvs/test.csv",
        timestamps_file="timestamp_csvs/test.csv")

    ball_splitter = DataSplitter(
        full_keypoint_file="ball_csvs/test.csv",  # placeholder
        timestamps_file="timestamp_csvs/test.csv")

    all_strokes = pose_splitter.get_splits_list()  # gives numpy array
    all_rallies = ball_splitter.get_splits_list(padding=False)

    # start pose estimation post process thread
    # ... (pose_process, args=(...))
    # start ball speed, position, trajectory coordinates thread
    # ... (ball_process, args=(...))

if __name__ == "__main__":
    main()
