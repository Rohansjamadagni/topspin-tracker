#!/usr/bin/env python3
import argparse
from pathlib import Path
import os
from multiprocessing import Process, Queue
import cv2
import depthai as dai
import numpy as np


labelMap = ['ball']

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', default="data", type=str, help="Path where to store the captured data")
args = parser.parse_args()

# Get the stored frames path
dest = Path(args.path).resolve().absolute()
frames = os.listdir(str(dest))
frames_sorted = sorted([int(i) for i in frames])

pipeline = dai.Pipeline()

left_in = pipeline.createXLinkIn()
right_in = pipeline.createXLinkIn()
rgb_in = pipeline.createXLinkIn()

left_in.setStreamName("left")
right_in.setStreamName("right")
rgb_in.setStreamName("rgbIn")

pipeline.setOpenVINOVersion(dai.OpenVINO.Version.VERSION_2021_1)

stereo = pipeline.createStereoDepth()
stereo.setConfidenceThreshold(240)
median = dai.StereoDepthProperties.MedianFilter.KERNEL_7x7
stereo.setMedianFilter(median)
stereo.setLeftRightCheck(False)
stereo.setExtendedDisparity(False)
stereo.setSubpixel(False)
stereo.setInputResolution(640,480)

left_in.out.link(stereo.left)
right_in.out.link(stereo.right)

right_s_out = pipeline.createXLinkOut()
right_s_out.setStreamName("rightS")
stereo.syncedRight.link(right_s_out.input)

left_s_out = pipeline.createXLinkOut()
left_s_out.setStreamName("leftS")
stereo.syncedLeft.link(left_s_out.input)

spatialDetectionNetwork = pipeline.createYoloSpatialDetectionNetwork()
spatialDetectionNetwork.setBlobPath("models/ball.blob")
spatialDetectionNetwork.setConfidenceThreshold(0.5)
spatialDetectionNetwork.input.setBlocking(False)
spatialDetectionNetwork.setBoundingBoxScaleFactor(0.3)
spatialDetectionNetwork.setDepthLowerThreshold(100)
spatialDetectionNetwork.setDepthUpperThreshold(5000)
#YOLO SPECIFIC
spatialDetectionNetwork.setNumClasses(1)
spatialDetectionNetwork.setCoordinateSize(4)
spatialDetectionNetwork.setAnchors(np.array([10,14, 23,27, 37,58, 81,82, 135,169, 344,319]))
spatialDetectionNetwork.setAnchorMasks({ "side26": np.array([1,2,3]), "side13": np.array([3,4,5]) })
spatialDetectionNetwork.setIouThreshold(0.5)

stereo.depth.link(spatialDetectionNetwork.inputDepth)
rgb_in.out.link(spatialDetectionNetwork.input)

bbOut = pipeline.createXLinkOut()
bbOut.setStreamName("bb")
spatialDetectionNetwork.boundingBoxMapping.link(bbOut.input)

detOut = pipeline.createXLinkOut()
detOut.setStreamName("det")
spatialDetectionNetwork.out.link(detOut.input)

depthOut = pipeline.createXLinkOut()
depthOut.setStreamName("depth")
spatialDetectionNetwork.passthroughDepth.link(depthOut.input)

rgbOut = pipeline.createXLinkOut()
rgbOut.setStreamName("rgb")
spatialDetectionNetwork.passthrough.link(rgbOut.input)

def to_planar(arr, shape):
    return cv2.resize(arr, shape).transpose(2, 0, 1).flatten()

# Pipeline defined, now the device is connected to
with dai.Device(pipeline) as device:
#    device.startPipeline()

    qLeft = device.getInputQueue('left')
    qRight = device.getInputQueue('right')
    qRgbIn = device.getInputQueue('rgbIn')

    qLeftS = device.getOutputQueue(name="leftS", maxSize=4, blocking=False)
    qRightS = device.getOutputQueue(name="rightS", maxSize=4, blocking=False)
    qDepth = device.getOutputQueue(name="depth", maxSize=4, blocking=False)

    qBb = device.getOutputQueue(name="bb", maxSize=4, blocking=False)
    qDet = device.getOutputQueue(name="det", maxSize=4, blocking=False)
    qRgbOut = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

    color = (255, 0, 0)
    # Read rgb/mono frames, send them to device and wait for the spatial object detection results
    for frame_folder in frames_sorted:
        files = os.listdir(str((Path(args.path) / str(frame_folder)).resolve().absolute()))
        # If there is no rgb/left/right frame in the folder, skip this "frame"
        print(files)
        if [f.startswith("color") or f.startswith("left") or f.startswith("right") for f in files].count(True) < 3: continue

        # Read the images from the FS
        images = [cv2.imread(str((Path(args.path) / str(frame_folder) / file).resolve().absolute()), cv2.IMREAD_GRAYSCALE if file.startswith("right") or file.startswith("left") else None) for file in files]
        for i in range(len(files)):
            right = files[i].startswith("right")
            if right or files[i].startswith("left"):
                h, w = images[i].shape
                frame = dai.ImgFrame()
                frame.setData(cv2.flip(images[i], 1)) # Flip the rectified frame
                frame.setType(dai.RawImgFrame.Type.RAW8)
                frame.setWidth(w)
                frame.setHeight(h)
                frame.setInstanceNum((2 if right else 1))
                if right: qRight.send(frame)
                else: qLeft.send(frame)

            # elif files[i].startswith("disparity"):
            #     cv2.imshow("original disparity", images[i])
            elif files[i].startswith("color"):
                preview = images[i][0:1080, 420:1500] # Crop before sending
                frame = dai.ImgFrame()
                frame.setType(dai.RawImgFrame.Type.BGR888p)
                frame.setData(to_planar(preview, (416, 416)))
                frame.setWidth(416)
                frame.setHeight(416)
                frame.setInstanceNum(0)
                qRgbIn.send(frame)
                #cv2.imshow("preview", preview)

        inRgb = qRgbOut.get()
        rgbFrame = inRgb.getCvFrame().reshape((416, 416, 3))

        cv2.imshow("left", qLeftS.get().getCvFrame())
        cv2.imshow("right", qRightS.get().getCvFrame())

        depthFrame = qDepth.get().getFrame()
        depthFrameColor = cv2.normalize(depthFrame, None, 255, 0, cv2.NORM_INF, cv2.CV_8UC1)
        depthFrameColor = cv2.equalizeHist(depthFrameColor)
        depthFrameColor = cv2.applyColorMap(depthFrameColor, cv2.COLORMAP_JET)

        height = inRgb.getHeight()
        width = inRgb.getWidth()

        inDet = qDet.tryGet()
        if inDet is not None:
            if len(inDet.detections) != 0:
                # Display boundingbox mappings on the depth frame
                bbMapping = qBb.get()
                roiDatas = bbMapping.getConfigData()
                for roiData in roiDatas:
                    roi = roiData.roi
                    roi = roi.denormalize(depthFrameColor.shape[1], depthFrameColor.shape[0])
                    topLeft = roi.topLeft()
                    bottomRight = roi.bottomRight()
                    xmin = int(topLeft.x)
                    ymin = int(topLeft.y)
                    xmax = int(bottomRight.x)
                    ymax = int(bottomRight.y)
                    cv2.rectangle(depthFrameColor, (xmin, ymin), (xmax, ymax), (0,255,0), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX)

            # Display (spatial) object detections on the color frame
            for detection in inDet.detections:
                # Denormalize bounding box
                x1 = int(detection.xmin * 416)
                x2 = int(detection.xmax * 416)
                y1 = int(detection.ymin * 416)
                y2 = int(detection.ymax * 416)
                try:
                    label = labelMap[detection.label]
                except:
                    label = detection.label
                cv2.putText(rgbFrame, str(label), (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
                cv2.putText(rgbFrame, "{:.2f}".format(detection.confidence*100), (x1 + 10, y1 + 35), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
                cv2.putText(rgbFrame, f"X: {int(detection.spatialCoordinates.x)} mm", (x1 + 10, y1 + 50), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
                cv2.putText(rgbFrame, f"Y: {int(detection.spatialCoordinates.y)} mm", (x1 + 10, y1 + 65), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
                cv2.putText(rgbFrame, f"Z: {int(detection.spatialCoordinates.z)} mm", (x1 + 10, y1 + 80), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)

                cv2.rectangle(rgbFrame, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX)

        cv2.imshow("rgb", rgbFrame)
        cv2.imshow("depth", depthFrameColor)

        if cv2.waitKey(1) == ord('q'):
            break

