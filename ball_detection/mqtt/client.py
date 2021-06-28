import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect('10.147.17.95', 1883)

client.publish("topspin/test", "Ball Detector Connected")
print('hi')
