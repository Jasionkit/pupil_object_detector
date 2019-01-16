# import the necessary packages
from threading import Thread
import datetime
import cv2

import argparse
import io

import zmq
from msgpack import unpackb, packb
import numpy as np

class pupilFixation:
	def __init__(self):

		addr = '127.0.0.1'  # remote ip or localhost
		req_port = "50020"  # same as in the pupil remote gui

		# open a req port to talk to pupil
		self.context = zmq.Context()
		
		self.req = self.context.socket(zmq.REQ)
		self.req.connect("tcp://{}:{}".format(addr, req_port))

		# ask for the sub port
		self.req.send_string('SUB_PORT')
		self.sub_port = self.req.recv_string()

		# open a sub port to listen to pupil
		self.sub = self.context.socket(zmq.SUB)
		self.sub.connect("tcp://{}:{}".format(addr, self.sub_port))

		# set subscriptions to topics
		# recv just fixation
		self.sub.setsockopt_string(zmq.SUBSCRIBE, 'fixation')
		
		topic, msg = self.recv_from_sub()

		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False

		self.fixation_norm_pos = None

		if topic == 'fixations':
			self.fixation_norm_pos = msg['norm_pos']


	def start(self):
		# start the thread to read frames from the video stream
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
		# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return
			# otherwise, read the next gaze information
			topic, msg = self.recv_from_sub()

			if topic == 'fixations':
				self.fixation_norm_pos = msg['norm_pos']

	def read(self):
		# return the fixation most recently read
		return self.fixation_norm_pos

	def stop(self):
 		# indicate that the thread should be stopped
 		self.stopped = True


	def recv_from_sub(self):
		'''Recv a message with topic, payload.
		Topic is a utf-8 encoded string. Returned as unicode object.
		Payload is a msgpack serialized dict. Returned as a python dict.
		'''
		topic = self.sub.recv_string()
		payload = unpackb(self.sub.recv(), encoding='utf-8')
		
		return topic, payload
