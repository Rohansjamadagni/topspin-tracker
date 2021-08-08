import paho.mqtt.client as mqtt
from csv_utils import CSV
import json
import sys
import os

class Ansible:
    def __init__(self):
        print("Initialising...")
        os.system('ansible-playbook -i ../ansible/hosts ../ansible/init.yml')

    @staticmethod
    def destroy(error=None):
        if error is not None:
            print(error)
        print("PACK BRO")
        os.system('ansible-playbook -i ../ansible/hosts ../ansible/packed.yml')
        exit()

    @staticmethod
    def ping(device):
        command = 'ansible all -m ping -v'
        p = subprocess.check_output(command.split(' '))

    @staticmethod
    def start_record():
        os.system('ansible-playbook -i ../ansible/hosts ../ansible/control.yml  &')

    @staticmethod
    def start_replay():
        os.system('ansible-playbook -i ../ansible/hosts ../ansible/replay.yml  &')

    @staticmethod
    def take_picture():
        os.system('ansible-playbook -i ../ansible/hosts.yml ../ansible/picture.yml')

class PoseCam(mqtt.Client, Ansible):
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
            self.destroy(contents)
        else:
            print(f'Wrong pose_{self.cam_number} topic')

    def __on_connect(self, contents):
        print(contents)

    def __on_coords(self, contents):
        csv_list = json.loads(contents)
        self.csv_obj.add_list(csv_list)

    def __on_rcv_frame_count(self, contents):
        print(f"Pose estimation frame number: {contents}")

    def __on_finish(self, contents):
        print(f"\n{contents}")

        self.csv_obj.filter_columns(window_length=5, polyorder=2,
                                columns=self._get_columns()[:-1], overwrite=True)

        self.csv_obj.save()
        print(f"Saved keypoint csv from {self.cam_number}")

class BallCam(mqtt.Client, Ansible):
    def __init__(
        self,
        cam_number: int):

        mqtt.Client.__init__(self)

        self.cam_number = cam_number

    def on_connect(self, client, userdata, detect_flags, rc):
        self.subscribe(f"ball/#")
        print(f"Connected to the ball topic!")
        print(f"Attempting to connect to ball camera")

    def on_message(self, client, ud, msg):
        contents = msg.payload.decode()

        if msg.topic == f'ball/connected':
            self.__on_connect(contents)
        elif msg.topic == f'ball/progress/record':
            self.__on_record(contents)
        elif msg.topic == f'ball/record/finished':
            self.__on_finish_record(contents)
        elif msg.topic == f'ball/progress/replay':
            self.__on_replay(contents)
        # receive data from ansible to start replay
        elif msg.topic == f'ball/replay/finished':
            self.__on_finish_replay(contents)
        elif msg.topic == f'ball/error':
            self.destroy(contents)
        else:
            print(f'Wrong ball topic')

    def __on_connect(self, contents):
        print(contents)
        # self.start_record()

    def __on_record(self, contents):
        print(f"Ball record frame number: {contents}")

    def __on_finish_record(self, contents):
        print(f"Done recording {contents} frames.")

    def __on_replay(self, contents):
        # ball detection on camera and generating final_result.csv
        print(f"Replay progress: {contents}")

    def __on_finish_replay(self, contents):
        # check for speed and ball location save to json.
        print(contents)

class Vibrator(mqtt.Client, Ansible):
    def __init__(
        self,
        cam_number: int,
        csv_dest: str):

        mqtt.Client.__init__(self)

        self.cam_number = cam_number
        self.csv_obj = CSV(filename=csv_dest, columns=['left', 'right'])

    def on_connect(self, client, userdata, detect_flags, rc):
        self.subscribe(f"vibration_{self.cam_number}/#")
        print(f"Connected to the vibration_{self.cam_number} topic!")
        print(f"Attempting to connect to vibration_{self.cam_number} camera")

    def on_message(self, client, ud, msg):
        contents = msg.payload.decode()

        if msg.topic == f'vibration_{self.cam_number}/connected':
            self.__on_connect(contents)
        elif msg.topic == f'vibration_{self.cam_number}/pitch':
            self.__on_vibration(contents)
        elif msg.topic == f'vibration_{self.cam_number}/finished':
            self.__on_finish(contents)
        elif msg.topic == f'vibration_{self.cam_number}/error':
            self.destroy(contents)
        else:
            print(f'Wrong vibration_{self.cam_number} topic')

    def __on_connect(self, contents):
        print(contents)

    def __on_vibration(self, contents):
        timestamp_list = json.loads(contents)
        self.csv_obj.add_list(timestamp_list)

    def __on_finish(self, contents):
        print(contents)
        self.csv_obj.save()
        print(f"Saved timestamp csv from {self.cam_number}")
