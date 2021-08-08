import RPi.GPIO as GPIO
import time
import json
import paho.mqtt.client as mqtt
import sys
import argparse
import os

os.system('echo 0 > ../flex.tape')

parser = argparse.ArgumentParser()

parser.add_argument("--cam", type=int,
                    help="Camera number")

args = parser.parse_args()

vib_1 = 21
vib_2 = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(vib_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(vib_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

broker_config = json.load(open('../ips.json', 'r'))
broker_ip = broker_config['broker_ip']
broker_port = broker_config['broker_port']

client = mqtt.Client()

try:
    client.connect(broker_ip, broker_port)
except:
    exit()

client.publish(f'vibration_{args.cam}/connected', json.dumps("Vibration sensors connected"))

TIME_THRESH = 1.6

def main():
    vib_list = []
    stroke_number = 1

    print("Vibrator started.")

    while True:
        if len(vib_list) == 0:
            if GPIO.input(vib_1) > 0:
                print("Vib 1")
                vib_list.append(time.time())

        if len(vib_list) == 1:
            if GPIO.input(vib_2) > 0 or (time.time()-vib_list[0] > TIME_THRESH):
                print("Vib 2")

                if time.time() - vib_list[0] > 1e-1:
                    vib_list.append(time.time())
                    client.publish(f'vibration_{args.cam}/pitch', json.dumps([vib_list]))

                    print(f"Duration of stroke: {vib_list[1] - vib_list[0]}")
                    print(f"Stroke number: {stroke_number}")

                    stroke_number += 1
                else:
                    print("Ignored.")

                vib_list = []

        f = open('../flex.tape', 'r')
        number = int(f.read()[0])

        if number == 1:
            break

        f.close()

    print("Vibrator terminated.")
    client.publish(f'vibration_{args.cam}/finished', json.dumps("Vibration sensors terminated"))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        client.publish(f'vibration_{args.cam}/error', json.dumps(e))
        exit()
