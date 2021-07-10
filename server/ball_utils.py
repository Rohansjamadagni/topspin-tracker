import json
import sys

def on_connect(contents):
    print("Ball detector camera connected")

def on_record(contents):
    sys.stdout.write(f"\rCurrent record frame number: {contents}")
    sys.stdout.flush()

def on_replay(contents):
    sys.stdout.write(f"\rCurrent replay frame number: {contents}")
    sys.stdout.flush()
