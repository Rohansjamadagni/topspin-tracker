import paho.mqtt.client as mqtt
import time

client = mqtt.Client()
client.connect('10.147.17.95', 1883)

while True:
    client.publish("topspin/test", "Pose Estimator Connected")
    time.sleep(1)
    print("POSE")

