import paho.mqtt.client as mqtt
import time

client = mqtt.Client()
client.connect('10.147.17.95', 1883)

while True:
    client.publish("topspin/test", "Ball Detector Connected")
    time.sleep(1)
    print("POSE")

