import RPi.GPIO as GPIO

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

def main():
    vib_list = []

    while True:
        if len(vib_list) == 0:
            if GPIO.input(vib_1) > 0:
                print("Vib 1")
                vib_list.append(time.time())

        if len(vib_list) == 1:
            if GPIO.input(vib_2) > 0 or (time.time()-t_1 > TIME_THRESH):
                print("Vib 2")
                vib_list.append(time.time())
                client.publish('pose/vibration', json.dumps([vib_list]))
                vib_list = []

if __name__ == "__main__":
    main()
