from __future__ import print_function
from utils.objDet_utils import *
from utils.pupilVideoStream import *
from utils.pupilFixation import *
import argparse
import multiprocessing
from multiprocessing import Queue, Pool
import cv2

def pupil_realtime(args):
    """
    Read and apply object detection to input real time stream (pupil)
    """

    # Set the multiprocessing logger to debug if required
    if args["logger_debug"]:
        logger = multiprocessing.log_to_stderr()
        logger.setLevel(multiprocessing.SUBDEBUG)

    # Multiprocessing: Init input and output Queue and pool of workers
    input_q = Queue(maxsize=args["queue_size"])
    output_q = Queue(maxsize=args["queue_size"])
    pool = Pool(args["num_workers"], worker, (input_q,output_q))

    # created a threaded video stream, another to Fixation and start the FPS counter
    vs = pupilVideoStream().start()
    gaze = pupilFixation().start()
    # fps = FPS().start()

    # Start reading and treating the video stream
    if args["display"] > 0:
        print()
        print("=====================================================================")
        print("Starting video acquisition. Press 'q' (on the video windows) to stop.")
        print("=====================================================================")
        print()

    while True:
        # Capture frame-by-frame
        ret, frame = vs.read()

        # Capture gaze norm position
        norm_pos = gaze.read()

        if ret and frame is not None and norm_pos is not None:
            
            # Queuing to Object detector
            input_q.put([frame,norm_pos])

            # Dequeuing frame 

            output_frame, object_detected = output_q.get()
            output_rgb = cv2.cvtColor(output_frame, cv2.COLOR_RGB2BGR)

            # Height and Width of the frama
            height, width, depth = frame.shape

            # Display the resulting frame
            if args["display"]:
                ## full screen
                if args["full_screen"]:
                    cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
                    cv2.setWindowProperty("frame",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

                # Set a circle around the gaze position
                cv2.circle(output_rgb,(int(norm_pos[0]*width),int(norm_pos[1]*height)),20, (0,255,0),3)

                object_detected = "Fixation object detected: " + str(object_detected)
                print("object_detected: {}".format(object_detected))
                cv2.putText(output_rgb, text = object_detected, org = (50, height-10),fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.5, color = (255,255,255))
                cv2.imshow("frame", output_rgb)

                # fps.update()

        else:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    #fps.stop()
    pool.terminate()
    vs.stop()
    gaze.stop()
    cv2.destroyAllWindows()

