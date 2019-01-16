import paho.mqtt.client as mqtt
import os
import time

class pupilToMqtt:
	def __init__(self):
		mqttc = mqtt.Client()

		mqttc.on_message = on_message
		mqttc.on_connect = on_connect
		mqttc.on_publish = on_publish
		mqttc.on_subscribe = on_subscribe

		mqttc.connect(host,port)

		mqttc.loop_start()

	def on_message(self):

	def on_connect(self):

	def on_publish(self):

	def publish_img(self):
		

