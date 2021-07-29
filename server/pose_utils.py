import paho.mqtt.client as mqtt
from csv_utils import CSV
import json
import sys
import os

class PoseCam(mqtt.Client):
    def __init__(
            self,
            cam_number: int,
            csv_dest: str):

        super(PoseCam, self).__init__()

        self.cam_number = cam_number
        self.csv_obj = CSV(filename=csv_dest, columns=self._get_columns())

    @staticmethod
    def _get_columns():
    	column_names = ['L-shoulder', 'R-shoulder',
    		   'L-elbow', 'R-elbow',
    		   'L-wrist', 'R-wrist']

    	divisions = ['X', 'Y', 'Z']

    	columns = []

    	for column in column_names:
    		for div in divisions:
    			columns.append(f'{column}-{div}')

    	columns.append('Timestamp')

    	return columns

    def on_connect(self, client, userdata, detect_flags, rc):
        self.subscribe(f"pose_{self.cam_number}/#")
        print(f"Connected to the pose_{self.cam_number} topic!")
        print(f"Attempting to connect to pose_{self.cam_number} camera")

    def on_message(self, client, ud, msg):
        contents = msg.payload.decode()

        if msg.topic == f'pose_{self.cam_number}/connected':
            self.__on_connect(contents)
        elif msg.topic == f'pose_{self.cam_number}/coords':
            self.__on_coords(contents)
        elif msg.topic == f'pose_{self.cam_number}/progress':
            self.__on_rcv_frame_count(contents)
        elif msg.topic == f'pose_{self.cam_number}/finished':
            self.__on_finish(contents)
        elif msg.topic == f'pose_{self.cam_number}/error':
            pack(contents)
        else:
            print(f'Wrong pose_{self.cam_number} topic')

    def __on_connect(self, contents):
        print(contents)

    def __on_coords(self, contents):
        csv_list = json.loads(self, contents)
        self.csv_obj.add_list(csv_list)

    def __on_rcv_frame_count(self, contents):
        sys.stdout.write(f"\rCurrent frame number: {contents}")
        sys.stdout.flush()

    def __on_finish(self, contents):
        print(f"\n{contents}")

        self.csv_obj.filter_columns(window_length=5, polyorder=2,
                                columns=kpt_cols[:-1], overwrite=True)

        self.csv_obj.save()
