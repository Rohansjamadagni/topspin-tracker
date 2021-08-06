import cv2
import pandas as pd
import numpy as np
import argparse
import time

from keypoint_utils import KeypointMapper

def make_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--video', '-v', default='', help='Enter path to video')
    parser.add_argument('--csv_file', '-cf', default='', help='Enter points file')
    parser.add_argument('--delay', '-d', type=float, default=0., help='Enter delay between each frame')
    parser.add_argument('--window_length', '-wl', type=int, default=0, help='Enter the window length to retrieve from csv file')
    parser.add_argument('--polyorder', '-p', type=int, default=0, help='Enter the polyorder to retrieve from csv file')
    parser.add_argument('--unfiltered', '-unf', default=False, action='store_true', help='Call this to view unfiltered mapping of points')
    parser.add_argument('--full', '-f', action='store_true', help='Call this to view full screen video')
    parser.add_argument('--hand', default='right')
    parser.add_argument('-o', '--output', default=None, type=str, help="Saves the output video to provided path")
    parser.add_argument('-bbg', '--black-background', action='store_true', help="Omit background or not")
    parser.add_argument('--pcolor', type=str, help="Enter joints mapping color")
    parser.add_argument('--lcolor', type=str, help="Enter stick (line) mapping color")
    parser.add_argument('-s', '--start', type=int, default=0, help="Enter frame to start from")

    args = parser.parse_args()

    assert args.video != ''
    assert args.csv_file != ''
    if args.window_length != 0:
        assert args.window_length > args.polyorder
        assert args.unfiltered != True

    return args

def main():
    args = make_args()

    if not args.full:
        cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    else:
        cv2.namedWindow('Image', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('Image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    mapper = KeypointMapper(
                    video=args.video,
                    csv_file=args.csv_file,
                    hand=args.hand,
                    filtered=not args.unfiltered)

    if args.output is not None:
        out = mapper.get_writer_object(args.output)

    for _ in range(0, args.start):
        ret, img = mapper.get_next()

    while True:
        ret, img = mapper.get_next()

        if not ret: break

        if args.black_background:
            img = np.zeros(img.shape, dtype=np.uint8)

        img = mapper.draw(img, pcolor=args.pcolor, lcolor=args.lcolor)
        cv2.imshow('Image', img)

        if args.output is not None:
            out.write(img)

        time.sleep(args.delay)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if args.output is not None:
        print(f'Video saved at {args.output}')
        out.release()

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
