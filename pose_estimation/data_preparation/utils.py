import os

import cv2
import pandas as pd
import numpy as np

class DataSplitter:
    def __init__(
        self,
        video,
        full_keypoint_file,
        timestamps_file
    ):
        self.vid = cv2.VideoCapture(video)

        self.main_df = pd.read_csv(full_keypoint_file, delimiter=',')
        self.ts_df = pd.read_csv(timestamps_file, delimiter=',')

    def generate_splits(
        self,
        csv_save_dir: str = None,
        video_save_dir: str = None,
        stroke_name: str = None
    ):
        assert csv_save_dir is not None

        if stroke_name is None:
            stroke_name = 'stroke'

        for idx, (start, stop) in enumerate(zip(self.ts_df['left'], self.ts_df['right'])):
            res = self.main_df.loc[(self.main_df['Timestamp'] >= left) & (self.main_df['Timestamp'] <= right)]
            res.to_csv(f"{csv_save_dir}/{stroke_name}_{idx}.csv")

            if video_save_dir is not None:
                out = self.get_writer_object(f"{video_save_dir}/{stroke_name}_{idx}.mp4")
                for i in res.index.tolist():
                    self.vid.set(1, i)
                    ret, frame = self.vid.read()
                    out.write(frame)
                out.release()

    def get_writer_object(self, output):
        vid_fps = self.vid.get(cv2.CAP_PROP_FPS)
        size = (int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output, fourcc, vid_fps, size)

        return out
