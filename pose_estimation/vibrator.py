import RPi.GPIO as GPIO
import time
import json
import paho.mqtt.client as mqtt
import sys
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

client.publish('vibration/connected', json.dumps("Vibration sensors connected"))

TIME_THRESH = 1.5

def main():
    vib_list = []

    print("Vibrator started.")

    while True:
        try:
            if len(vib_list) == 0:
                if GPIO.input(vib_1) > 0:
                    print("Vib 1")
                    vib_list.append(time.time())

            if len(vib_list) == 1:
                if GPIO.input(vib_2) > 0 or (time.time()-vib_list[0] > TIME_THRESH):
                    print("Vib 2")
                    vib_list.append(time.time())
                    client.publish('vibration/pitch', json.dumps([vib_list]))
                    vib_list = []
        except KeyboardInterrupt:
            save_data()
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Vibrator terminated.")
        client.publish('vibration/finished', json.dumps("Vibration sensors terminated"))
        exit()
    except Exception as e:
        client.publish(f'vibration/error', json.dumps(e))
        exit()
