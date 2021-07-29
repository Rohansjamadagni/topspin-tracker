import json
import sys
import os

from csv_utils import CSV

vibration_csv = CSV(filename="timestamp_csvs/2_test.csv", columns=['left', 'right'])

def on_connect(contents):
    print(contents)

def on_vibration(contents):
    timestamp_list = json.loads(contents)
    vibration_csv.add_list(timestamp_list)
    vibration_csv.save()

def on_finish(contents):
    vibration_csv.save()
