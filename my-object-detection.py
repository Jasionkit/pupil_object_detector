'''
(*)------------------------------------------------------------
Pupil - eye Object detection and gaze tracking

Acrossing 2019
------------------------------------------------------------(*)
'''

from __future__ import print_function
from function.pupil_realtime import *
import argparse
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

if __name__ == '__main__':

    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--display", type=int, default=0,
	            help="Whether or not frames should be displayed")
    ap.add_argument('-w', '--num-workers', dest='num_workers', type=int,
                        default=2, help='Number of workers.')
    ap.add_argument('-q-size', '--queue-size', dest='queue_size', type=int,
                        default=5, help='Size of the queue.')
    ap.add_argument('-l', '--logger-debug', dest='logger_debug', type=int,
                        default=0, help='Print logger debug')
    ap.add_argument('-f', '--fullscreen', dest='full_screen', type=int,
                        default=0, help='enable full screen')
    args = vars(ap.parse_args())

    pupil_realtime(args)
