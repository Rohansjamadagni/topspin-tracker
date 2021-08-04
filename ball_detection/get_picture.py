"""
This example shows usage of Camera Control message as well as ColorCamera configInput to change crop x and y
Uses 'WASD' controls to move the crop window, 'C' to capture a still image, 'T' to trigger autofocus, 'IOKL,.'
for manual exposure/focus:
  Control:      key[dec/inc]  min..max
  exposure time:     I   O      1..33000 [us]
  sensitivity iso:   K   L    100..1600
  focus:             ,   .      0..255 [far..near]
To go back to auto controls:
  'E' - autoexposure
  'F' - autofocus (continuous)
"""

import depthai as dai
import cv2
import sys
import os

if not os.path.isdir('pictures'):
  os.system("mkdir pictures")

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
camRgb = pipeline.createColorCamera()
videoEncoder = pipeline.createVideoEncoder()
stillEncoder = pipeline.createVideoEncoder()

controlIn = pipeline.createXLinkIn()
configIn = pipeline.createXLinkIn()
videoMjpegOut = pipeline.createXLinkOut()
stillMjpegOut = pipeline.createXLinkOut()
previewOut = pipeline.createXLinkOut()

controlIn.setStreamName('control')
configIn.setStreamName('config')
videoMjpegOut.setStreamName('video')
stillMjpegOut.setStreamName('still')
previewOut.setStreamName('preview')

# Properties
camRgb.setVideoSize(640, 360)
camRgb.setPreviewSize(300, 300)
videoEncoder.setDefaultProfilePreset(camRgb.getVideoSize(), camRgb.getFps(), dai.VideoEncoderProperties.Profile.MJPEG)
stillEncoder.setDefaultProfilePreset(camRgb.getStillSize(), 1, dai.VideoEncoderProperties.Profile.MJPEG)

# Linking
camRgb.video.link(videoEncoder.input)
camRgb.still.link(stillEncoder.input)
camRgb.preview.link(previewOut.input)
controlIn.out.link(camRgb.inputControl)
configIn.out.link(camRgb.inputConfig)
videoEncoder.bitstream.link(videoMjpegOut.input)
stillEncoder.bitstream.link(stillMjpegOut.input)

# Connect to device and start pipeline
focus_timer = 0
with dai.Device(pipeline) as device:

    # Get data queues
    controlQueue = device.getInputQueue('control')
    stillQueue = device.getOutputQueue('still')


    while True:
        print(focus_timer)
        ctrl = dai.CameraControl()
        ctrl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.AUTO)
        ctrl.setCaptureStill(True)
        controlQueue.send(ctrl)

        stillFrames = stillQueue.tryGetAll()
        print(len(stillFrames))
        if stillFrames and focus_timer > 200:
            for stillFrame in stillFrames:
                frame = cv2.imdecode(stillFrame.getData(), cv2.IMREAD_UNCHANGED)
                cv2.imwrite('pictures/table_image.png', frame)
                sys.exit(0)
        focus_timer += 1
