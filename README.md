# Object-detection

Apply tensorflow object detection on input video stream.

# To use it:

Clone repo in your working directory

Build docker image:

> docker build -t realtime-objectdetection .

Configure script (see bellow)

Launch script:

> bash runDocker.sh

# To configure it:

Configuration is made in exec.sh at python function call:

> python3 my-object-detection.py ...

All possible arguments are:

```

-d (--display), type=int, default=0: Whether or not frames should be displayed

-f (--fullscreen), type=int, default=0: Enable full screen

-w (--num-workers), type=int, default=2: Number of workers

-q-size (--queue-size), type=int, default=5: Size of the queue

-l (--logger-debug), type=int, default=0: Print logger debug

```
