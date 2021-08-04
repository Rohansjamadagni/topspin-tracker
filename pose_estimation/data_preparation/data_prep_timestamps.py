import os
import argparse
import time

import sys
sys.path.append('..')

from utils import DataSplitter
from visualise.keypoint_utils import KeypointMapper

import cv2
import pandas as pd
import numpy as np

def make_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--video', '-v', default='',
                        help='Enter path to video')

    parser.add_argument('--csv_file', '-cf', default='',
                        help='Enter points file')
    parser.add_argument('--timestamps_file', '-tf', default='',
                        help='Enter timestamps file')

    parser.add_argument('--csv_output_dir', '-co', default='',
                        help='Enter stroke directory')
    parser.add_argument('--video_output_dir', '-vo', default=None, type=str,
                        help="Saves the output video to provided path")

    parser.add_argument('--stroke_name', default=None, type=str,
                        help="Provide a single stroke name that has been played for data collection")

    args = parser.parse_args()

    assert args.video != ''
    assert args.csv_file != ''
    assert args.timestamps_file != ''

    assert args.csv_output_dir != ''
    if not os.path.isdir(args.csv_output_dir):
        os.makedirs(args.csv_output_dir)

    if args.video_output_dir is not None and not os.path.isdir(args.video_output_dir):
        os.makedirs(args.video_output_dir)

    return args

def main():
    args = make_args()

    splitter = DataSplitter(
                    video=args.video,
                    main_csv_file=args.csv_file,
                    timestamps_file=args.timestamps_file)

    splitter.generate_split_csvs(
        csv_save_dir=args.csv_output_dir,
        video_save_dir=args.video_output_dir,
        stroke_name=args.stroke_name
    )

    print(f"Generated csv splits at: {args.csv_output_dir}")
    print(f"Generated video splits at: {args.video_output_dir}")

if __name__ == "__main__":
    main()
