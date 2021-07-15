# To Run Pose Estimation

## Server Side

Start the subscriber
```
python3 subscriber.py
```

Folder structure for server
```
server
    ├── keypoint_csvs
    ├── timestamp_csvs
    ├── *_utils.py
    ├── subscriber.py
```
Here keypoint_csvs and timestamp_csvs must exist

To change the csv names and destinations, or to give it as a command line argument, make appropriate changes to `pose_utils.py` at `line 8` and `line 11`

## Client Side (RPi)

Start the camera pose estimation

```sh
python3 run_pose_estimation.py --lm_m 831 -o <video_name>.mp4 --internal_fps 25
```
To change where the video is saved, go to `run_pose_estimation.py` at `line 87`. <br>
The `--lm_m` argument tells which model to use. The options are `full`, `lite` and `831`. `831` seems to be the best balance between fps and accuracy but feel free to change it. Stick to only one model for data collection though.

## Data Preparation

After recording the video, splits need to be generated player-wise and inside that, stroke-wise.

```sh
python3 data_prep_timestamps.py -v <path to video> -cf <path to keypoint csv> -tf <path to timestamps csv> -co <path to folder where csv splits should be saved>  -vo <path to folder where video splits will be saved> --stroke_name <stroke played in the video>
```

Play one single stroke throughout one video so that it will be easier to clean and label for further model training.

Preferable folder structure for the splits:

CSVs:
```
csvs
    ├── player1
        ├── <stroke_1_name>
            ├── --all csv files--
        ├── <stroke_2_name>
             .
             .
             .
    ├── player2
        .
        .
        .
```
Videos:
```
videos
    ├── player1
        ├── <stroke_1_name>
            ├── --all csv files--
        ├── <stroke_2_name>
             .
             .
             .
    ├── player2
        .
        .
        .
```
