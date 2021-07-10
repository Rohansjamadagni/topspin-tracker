import json
import sys

def on_connect(contents):
    print("Ball detector camera connected")

def on_record(contents):
    sys.stdout.write(f"\rCurrent record frame number: {contents}")

def on_record(contents):
    sys.stdout.write(f"\rCurrent frame number: {contents}")
