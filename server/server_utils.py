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

class BallCam(mqtt.Client, Ansible):
    def __init__(
        self,
        cam_number: int):

        mqtt.Client.__init__(self)

        self.cam_number = cam_number

    def on_connect(self, client, userdata, detect_flags, rc):
        self.subscribe(f"ball_{self.cam_number}/#")
        print(f"Connected to the ball_{self.cam_number} topic!")
        print(f"Attempting to connect to ball_{self.cam_number} camera")

    def on_message(self, client, ud, msg):
        contents = msg.payload.decode()

        if msg.topic == f'ball_{self.cam_number}/connected':
            self.__on_connect(contents)
        elif msg.topic == f'ball_{self.cam_number}/progress/record':
            self.__on_record(contents)
        elif msg.topic == f'ball_{self.cam_number}/record/finished':
            self.__on_finish_record(contents)
        elif msg.topic == f'ball_{self.cam_number}/progress/replay':
            self.__on_replay(contents)
        # receive data from ansible to start replay
        elif msg.topic == f'ball_{self.cam_number}/replay/finished':
            self.__on_finish_replay(contents)
        elif msg.topic == f'ball_{self.cam_number}/error':
            self.destroy(contents)
        else:
            print(f'Wrong ball_{self.cam_number} topic')

    def __on_connect(contents):
        pass

    def __on_record(contents):
        pass

    def __on_finish_record(contents):
        pass

    def __on_replay(contents):
        pass

    def __on_finish_replay(contents):
        pass

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

    def on_message_vib(self, client, ud, msg):
        contents = msg.payload.decode()

        if msg.topic == f'vibration_{self.cam_number}/connected':
            self.__on_connect(contents)
        elif msg.topic == f'vibration_{self.cam_number}/pitch':
            self.__on_vibration(contents)
        elif msg.topic == f'vibration_{self.cam_number}/finished':
            self.__on_finish(contents)
        elif msg.topic == f'vibration_{self.cam_number}/error':
            pack(contents)
        else:
            print(f'Wrong vibration_{self.cam_number} topic')

    def __on_connect(contents):
        print(contents)

    def __on_vibration(contents):
        timestamp_list = json.loads(contents)
        self.csv_obj.add_list(timestamp_list)

    def __on_finish(contents):
        print(contents)
        self.csv_obj.save()
