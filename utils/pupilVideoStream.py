# import the necessary packages
from threading import Thread
import datetime
import cv2

import argparse
import io

import zmq
from msgpack import unpackb, packb
import numpy as np

class FPS:
    def __init__(self):
        # store the start time, end time, and total number of frames
        # that were examined between the start and end intervals
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self):
        # start the timer
        self._start = datetime.datetime.now()
        return self
    
    def stop(self):
        # stop the timer
        self._end = datetime.datetime.now()

    def update(self):
        # increment the total number of frames examined during the
        # start and end intervals
        self._numFrames += 1

    def elapsed(self):
        # return the total number of seconds between the start and
        # end interval
        self._end = datetime.datetime.now()

        return (self._end - self._start).total_seconds()

    def fps(self):
        # compute the (approximate) frames per second
        return self._numFrames / self.elapsed()

class pupilVideoStream:
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

		# Start frame publisher with format BGR
		self.notify({'subject': 'start_plugin', 'name': 'Frame_Publisher', 'args': {'format': 'bgr'}})

		# open a sub port to listen to pupil
		self.sub = self.context.socket(zmq.SUB)
		self.sub.connect("tcp://{}:{}".format(addr, self.sub_port))

		# set subscriptions to topics
		# recv frame.world
		self.sub.setsockopt_string(zmq.SUBSCRIBE, 'frame.world')
		topic, msg = self.recv_from_sub()

		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False

		self.grabbed = False
		self.frame = None

		if topic == 'frame.world':
			self.grabbed = True
			self.frame = np.frombuffer(msg['__raw_data__'][0], dtype=np.uint8).reshape(msg['height'], msg['width'], 3)

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
			# otherwise, read the next frame from the stream
			topic, msg = self.recv_from_sub()

			if topic == 'frame.world':
				self.grabbed = True
				self.frame = np.frombuffer(msg['__raw_data__'][0], dtype=np.uint8).reshape(msg['height'], msg['width'], 3)

	def read(self):
		# return the frame most recently read
		return self.grabbed, self.frame

	def stop(self):
 		# indicate that the thread should be stopped
 		self.stopped = True

	# send notification:
	def notify( self, notification):
		"""Sends ``notification`` to Pupil Remote"""
		topic = 'notify.' + notification['subject']
		payload = packb(notification, use_bin_type=True)
		self.req.send_string(topic, flags=zmq.SNDMORE)
		self.req.send(payload)
		return self.req.recv_string()

	def recv_from_sub(self):
		'''Recv a message with topic, payload.
		Topic is a utf-8 encoded string. Returned as unicode object.
		Payload is a msgpack serialized dict. Returned as a python dict.
		Any addional message frames will be added as a list
		in the payload dict with key: '__raw_data__' .
		'''
		topic = self.sub.recv_string()
		payload = unpackb(self.sub.recv(), encoding='utf-8')
		extra_frames = []
		while self.sub.get(zmq.RCVMORE):
			extra_frames.append(self.sub.recv())
		if extra_frames:
			payload['__raw_data__'] = extra_frames
		return topic, payload
