#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow.keras as K

import sys
sys.path.insert(0, '..')
from pose_estimation.data_preparation.utils import DataSplitter

def _get_columns():
    column_names = ['L-shoulder', 'R-shoulder',
                'R-elbow',
                'R-wrist']

    divisions = ['X', 'Y', 'Z']

    columns = []

    for column in column_names:
        for div in divisions:
            columns.append(f'{column}-{div}')

    return columns

def get_stroke_preds(session):
    '''
    Uses the session number to read required csvs and send them
    to the stroke recognition NN for inference
    '''

    columns = _get_columns()

    FRAME_THRESHOLD = 30
    NUM_PTS = len(columns)

    kpt_csv1 = f'keypoint_csvs/cam_1/session_{session}.csv'
    kpt_csv2 = f'keypoint_csvs/cam_2/session_{session}.csv'

    vib_csv = f'timestamp_csvs/session_{session}.csv'

    splitter_1 = DataSplitter(main_csv_file=kpt_csv1, timestamps_file=vib_csv)
    splitter_2 = DataSplitter(main_csv_file=kpt_csv2, timestamps_file=vib_csv)

    cam_1 = splitter_1.get_splits_list(columns=columns)
    cam_2 = splitter_2.get_splits_list(columns=columns)

    strokes = np.empty((0, 30, 24))

    for st1, st2 in zip(cam_1, cam_2):
        st1 = st1.reshape((-1, 12))
        st2 = st2.reshape((-1, 12))

        while st1.shape[0] < FRAME_THRESHOLD:
                st1 = np.append(st1, np.array([[0 for _ in range(0, NUM_PTS)]]), axis=0)
        while st2.shape[0] < FRAME_THRESHOLD:
                st2 = np.append(st2, np.array([[0 for _ in range(0, NUM_PTS)]]), axis=0)

        st1 = st1[:30]
        st2 = st2[:30]

        combined = np.dstack([st1, st2])
        combined = combined.reshape((1, -1, 24))

        strokes = np.append(strokes, combined, axis=0)

    # print(strokes.shape)
    strokes = strokes.astype(np.float32)

    model = K.models.load_model('models/stroke_recognition.h5')

    preds = model.predict(strokes)
    preds = np.argmax(preds, axis=1)
    # print(preds.shape)

    return preds

def main():
    log = open('sessions.log', 'r')
    session = int(log.readlines()[-1][0])

    preds = get_stroke_preds(session)

    print(preds[:10])

if __name__ == "__main__":
    main()
