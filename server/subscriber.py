# subscriber
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect('10.147.17.95', 1883)

def on_connect(client, userdata, flags, rc):
    print("Connected to a broker!")
    client.subscribe("topspin/test")

def on_message(client, userdata, message):
    if(message.payload.decode() == "Ball Detector Connected"):
        print("Ball detector connected")
    if(message.payload.decode() == "Pose Estimator Connected"):
        print("Pose Estimator connected")

while True:
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()