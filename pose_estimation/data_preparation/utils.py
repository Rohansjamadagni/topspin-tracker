import os

import cv2
import pandas as pd
import numpy as np

class DataSplitter:
    def __init__(
        self,
        main_csv_file,
        timestamps_file,
        video=None,
    ):

        self.main_df = pd.read_csv(main_csv_file, delimiter=',')
        self.ts_df = pd.read_csv(timestamps_file, delimiter=',')

        if video is not None:
            self.vid = cv2.VideoCapture(video)

    def generate_split_csvs(
        self,
        csv_save_dir: str = None,
        video_save_dir: str = None,
        stroke_name: str = None
    ):
        assert csv_save_dir is not None

        if stroke_name is None:
            stroke_name = 'stroke'

        for idx, (left, right) in enumerate(zip(self.ts_df['left'], self.ts_df['right'])):
            res = self.main_df.loc[(self.main_df['Timestamp'] >= left) & (self.main_df['Timestamp'] <= right)]
            idxs = res.index.tolist()

            for _ in range(0, 5):
                idxs.append(idxs[-1] + 1)
                idxs.pop(0)

            res = self.main_df.loc[idxs]

            res.to_csv(f"{csv_save_dir}/{stroke_name}_{idx+1}.csv")

            if video_save_dir is not None:
                out = self.get_writer_object(f"{video_save_dir}/{stroke_name}_{idx+1}.mp4")
                for i in idxs: #res.index.tolist():
                    self.vid.set(1, i)
                    ret, frame = self.vid.read()
                    out.write(frame)
                out.release()

    def get_splits_list(
                self,
                columns: list) -> np.ndarray:

        """
        Generates splits based on timestamps and returns an array with all the splits from the main_csv_file

        Parameters
        ----------
        columns: list
            columns to get from the csv file

        Returns
        -------
        numpy.ndarray containing all splits
        """

        splits = []

        for idx, (left, right) in enumerate(zip(self.ts_df['left'], self.ts_df['right'])):
            res = self.main_df.loc[(self.main_df['Timestamp'] >= left) & (self.main_df['Timestamp'] <= right)]

            split = np.asarray(res[columns].values.tolist())

            splits.append(split)

        return np.asarray(splits, dtype=object)

    def generate_range_csv(
        self,
        csv_save_dir: str = None
    ):
        assert csv_save_dir is not None

        cols = ['stroke_number', 'range_start', 'range_stop']

        df = pd.DataFrame(columns=cols)
        df.to_csv(f"{csv_save_dir}/ranges.csv")

        for idx, (left, right) in enumerate(zip(self.ts_df['left'], self.ts_df['right'])):
            res = self.main_df.loc[(self.main_df['Timestamp'] >= left) & (self.main_df['Timestamp'] <= right)]
            idxs = res.index.tolist()

            df = df.append({
                'stroke_number': idx+1,
                'range_start': idxs[0],
                'range_stop': idxs[-1]
                }, ignore_index=True)

        df.to_csv(f"{csv_save_dir}/ranges.csv", mode='a', header=False)

    def get_writer_object(self, output):
        vid_fps = self.vid.get(cv2.CAP_PROP_FPS)
        size = (int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output, fourcc, vid_fps, size)

        return out
