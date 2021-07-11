#!/usr/bin/env python3
import argparse
from pathlib import Path
from time import monotonic
from multiprocessing import Process, Queue
import cv2
import depthai as dai
from datetime import datetime
import paho.mqtt.client as mqtt
import json
import sys

meta_data_ = open('ips.json', 'r')
meta_data = json.load(meta_data_)
meta_data = meta_data['meta_data']

broker_ip = json.load(open('../ips.json', 'r'))['broker']

client = mqtt.Client()
# connection refused if fails
try:
    client.connect(broker_ip, 1883)
except:
    # exit if fails
    sys.exit(1)

meta_data['device_connected'] = True
client.publish("topspin/test", json.dumps(meta_data))

def check_range(min_val, max_val):
    def check_fn(value):
        ivalue = int(value)
        if min_val <= ivalue <= max_val:
            return ivalue
        else:
            raise argparse.ArgumentTypeError(
                "{} is an invalid int value, must be in range {}..{}".format(value, min_val, max_val)
            )
    return check_fn

def get_path_name():
    f = open('filenames.txt', 'a+')
    filename_ = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    filename_ = '../data/data-' + filename_
    f.write(filename_ +'\n')
    return str(filename_)

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--threshold', default=0.3, type=float, help="Maximum difference between packet timestamps to be considered as synced")
parser.add_argument('-p', '--path', default=get_path_name(), type=str, help="Path where to store the captured data")
parser.add_argument('-d', '--dirty', action='store_true', default=False, help="Allow the destination path not to be empty")
# parser.add_argument('-nd', '--no-debug', dest="prod", action='store_true', default=False, help="Do not display debug output")
parser.add_argument('-m', '--time', type=float, default=float("inf"), help="Finish execution after X seconds")
parser.add_argument('-af', '--autofocus', type=str, default=None, help="Set AutoFocus mode of the RGB camera", choices=list(filter(lambda name: name[0].isupper(), vars(dai.CameraControl.AutoFocusMode))))
parser.add_argument('-mf', '--manualfocus', type=check_range(0, 255), help="Set manual focus of the RGB camera [0..255]")
parser.add_argument('-et', '--exposure-time', type=check_range(1, 33000), help="Set manual exposure time of the RGB camera [1..33000]")
parser.add_argument('-ei', '--exposure-iso', type=check_range(100, 1600), help="Set manual exposure ISO of the RGB camera [100..1600]")

parser.add_argument('-nd', '--no-depth', action='store_true', default=False, help="Do not save depth map. If set, mono frames will be saved")
parser.add_argument('-mono', '--mono', action='store_true', default=True, help="Save mono frames")
parser.add_argument('-e', '--encode', action='store_true', default=True, help="Encode mono frames into jpeg. If set, it will enable -mono as well")

args = parser.parse_args()

try:
    exposure = [args.exposure_time, args.exposure_iso]
    if any(exposure) and not all(exposure):
        raise RuntimeError("Both --exposure-time and --exposure-iso needs to be provided")

    SAVE_MONO = args.encode or args.mono or args.no_depth

    dest = Path(args.path).resolve().absolute()
    dest_count = len(list(dest.glob('*')))
    if dest.exists() and dest_count != 0 and not args.dirty:
        raise ValueError(f"Path {dest} contains {dest_count} files. Either specify new path or use \"--dirty\" flag to use current one")
    dest.mkdir(parents=True, exist_ok=True)

    pipeline = dai.Pipeline()

    rgb = pipeline.createColorCamera()

    rgb.setPreviewKeepAspectRatio(keep=False)
    rgb.setPreviewSize(416, 416)
    rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
    rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    rgb.setInterleaved(False)
    rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
    rgb.setFps(90)

    # Create output for the rgb
    rgbOut = pipeline.createXLinkOut()
    rgbOut.setStreamName("color")

    rgb_encoder = pipeline.createVideoEncoder()
    rgb_encoder.setDefaultProfilePreset(rgb.getVideoSize(), rgb.getFps(), dai.VideoEncoderProperties.Profile.MJPEG)
    rgb_encoder.setLossless(False)
    rgb.video.link(rgb_encoder.input)
    rgb_encoder.bitstream.link(rgbOut.input)

    # Create mono cameras
    left = pipeline.createMonoCamera()
    left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    left.setBoardSocket(dai.CameraBoardSocket.LEFT)
    left.setFps(50)

    right = pipeline.createMonoCamera()
    right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
    right.setFps(50)

    stereo = pipeline.createStereoDepth()
    stereo.setConfidenceThreshold(240)
    median = dai.StereoDepthProperties.MedianFilter.KERNEL_7x7
    stereo.setMedianFilter(median)
    stereo.setLeftRightCheck(False)
    stereo.setExtendedDisparity(False)
    stereo.setSubpixel(False)

    left.out.link(stereo.left)
    right.out.link(stereo.right)

    if not args.no_depth:
        depthOut = pipeline.createXLinkOut()
        depthOut.setStreamName("depth")
        stereo.depth.link(depthOut.input)

    controlIn = pipeline.createXLinkIn()
    controlIn.setStreamName('control')
    controlIn.out.link(rgb.inputControl)

    # Create output
    if SAVE_MONO:
        leftOut = pipeline.createXLinkOut()
        leftOut.setStreamName("left")
        rightOut = pipeline.createXLinkOut()
        rightOut.setStreamName("right")
        if args.encode:
            left_encoder = pipeline.createVideoEncoder()
            left_encoder.setDefaultProfilePreset(left.getResolutionSize(), left.getFps(), dai.VideoEncoderProperties.Profile.MJPEG)
            left_encoder.setLossless(False)
            stereo.rectifiedLeft.link(left_encoder.input)
            left_encoder.bitstream.link(leftOut.input)

            right_encoder = pipeline.createVideoEncoder()
            right_encoder.setDefaultProfilePreset(right.getResolutionSize(), right.getFps(), dai.VideoEncoderProperties.Profile.MJPEG)
            right_encoder.setLossless(False)
            stereo.rectifiedRight.link(right_encoder.input)
            right_encoder.bitstream.link(rightOut.input)
        else:
            stereo.rectifiedLeft.link(leftOut.input)
            stereo.rectifiedRight.link(rightOut.input)

    # https://stackoverflow.com/a/7859208/5494277
    def step_norm(value):
        return round(value / args.threshold) * args.threshold


    def seq(packet):
        return packet.getSequenceNum()


    def tst(packet):
        return packet.getTimestamp().total_seconds()


    # https://stackoverflow.com/a/10995203/5494277
    def has_keys(obj, keys):
        return all(stream in obj for stream in keys)


    class PairingSystem:
        seq_streams = []
        if SAVE_MONO:
            seq_streams.append("left")
            seq_streams.append("right")
        if not args.no_depth:
            seq_streams.append("depth")
        print(seq_streams)
        ts_streams = ["color"]
        seq_ts_mapping_stream = seq_streams[0]

        def __init__(self):
            self.ts_packets = {}
            self.seq_packets = {}
            self.last_paired_ts = None
            self.last_paired_seq = None

        def add_packets(self, packets, stream_name):
            if packets is None:
                return
            if stream_name in self.seq_streams:
                for packet in packets:
                    seq_key = seq(packet)
                    self.seq_packets[seq_key] = {
                        **self.seq_packets.get(seq_key, {}),
                        stream_name: packet
                    }
            elif stream_name in self.ts_streams:
                for packet in packets:
                    ts_key = step_norm(tst(packet))
                    self.ts_packets[ts_key] = {
                        **self.ts_packets.get(ts_key, {}),
                        stream_name: packet
                    }

        def get_pairs(self):
            results = []
            for key in list(self.seq_packets.keys()):
                if has_keys(self.seq_packets[key], self.seq_streams):
                    ts_key = step_norm(tst(self.seq_packets[key][self.seq_ts_mapping_stream]))
                    if ts_key in self.ts_packets and has_keys(self.ts_packets[ts_key], self.ts_streams):
                        results.append({
                            **self.seq_packets[key],
                            **self.ts_packets[ts_key]
                        })
                        self.last_paired_seq = key
                        self.last_paired_ts = ts_key
            if len(results) > 0:
                self.collect_garbage()
            return results

        def collect_garbage(self):
            for key in list(self.seq_packets.keys()):
                if key <= self.last_paired_seq:
                    del self.seq_packets[key]
            for key in list(self.ts_packets.keys()):
                if key <= self.last_paired_ts:
                    del self.ts_packets[key]

    frame_q = Queue()

    folder_num = 0
    def store_frames(in_q):
        global folder_num
        def save_png(frames_path, name, item):
            cv2.imwrite(str(frames_path / Path(f"{stream_name}.png")), item)
        def save_jpeg(frames_path, name, item):
            with open(str(frames_path / Path(f"{stream_name}.jpeg")), "wb") as f:
                f.write(bytearray(item))
        def save_depth(frames_path, name, item):
            with open(str(frames_path / Path(f"{stream_name}")), "wb") as f:
                f.write(bytearray(item))
        while True:
            frames_dict = in_q.get()
            if frames_dict is None:
                return
            frames_path = dest / Path(str(folder_num))
            folder_num = folder_num + 1
            frames_path.mkdir(parents=False, exist_ok=False)

            for stream_name, item in frames_dict.items():
                if stream_name == "depth": save_depth(frames_path, stream_name, item)
                elif stream_name == "color": save_jpeg(frames_path, stream_name, item)
                elif args.encode: save_jpeg(frames_path, stream_name, item)
                else: save_png(frames_path, stream_name, item)

    store_p = Process(target=store_frames, args=(frame_q, ))
    store_p.start()
    ps = PairingSystem()
    count = 0
    # Pipeline defined, now the device is connected to
    with dai.Device(pipeline) as device:

        qControl = device.getInputQueue('control')

        ctrl = dai.CameraControl()
        if args.autofocus:
            ctrl.setAutoFocusMode(getattr(dai.CameraControl.AutoFocusMode, args.autofocus))
        if args.manualfocus:
            ctrl.setManualFocus(args.manualfocus)
        if all(exposure):
            ctrl.setManualExposure(*exposure)

        qControl.send(ctrl)

        cfg = dai.ImageManipConfig()

        start_ts = monotonic()
        # set flag for record
        meta_data['device_status']['record']['flag'] = True

        while True:
            for queueName in PairingSystem.seq_streams + PairingSystem.ts_streams:
                ps.add_packets(device.getOutputQueue(queueName).tryGetAll(), queueName)

            pairs = ps.get_pairs()
            for pair in pairs:
                obj = {"color": pair["color"].getData() }
                if SAVE_MONO:
                    if args.encode:
                        obj["left"] = pair["left"].getData()
                        obj["right"] = pair["right"].getData()
                    else:
                        obj["left"] = pair["left"].getCvFrame()
                        obj["right"] = pair["right"].getCvFrame()
                if not args.no_depth:
                    obj["depth"] = pair["depth"].getFrame()

                frame_q.put(obj)
                if count % 60 == 0:
                    # publish count
                    meta_data['device_status']['record']['frame_count'] = count
                    client.publish("topspin/test", json.dumps(meta_data))
                count += 1

            if cv2.waitKey(1) == ord('q'):
                break

            if monotonic() - start_ts > args.time:
                break

    frame_q.put(None)
    store_p.join()
    meta_data['device_status']['record']['frame_count'] = count
    meta_data['device_status']['record']['flag'] = False
    meta_data['device_status']['record']['completed'] = True
    client.publish("topspin/test", json.dumps(meta_data))
except Exception as e:
    meta_data['failure']['status'] = True
    meta_data['failure']['error'] = str(e)
    client.publish("topspin/test", json.dumps(meta_data))
    print(e)
