import os
from utils.pupilVideoStream import *
import numpy as np
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util


# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = 'model/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = 'model/mscoco_label_map.pbtxt'

NUM_CLASSES = 90

# Loading label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)

def detect_objects(image_np, sess, detection_graph, norm_pos, height, width):
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Each box represents a part of the image where a particular object was detected.
    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # Each score represent how level of confidence for each of the objects.
    # Score is shown on the result image, together with the class label.
    scores = detection_graph.get_tensor_by_name('detection_scores:0')
    classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # Actual detection.
    (boxes, scores, classes, num_detections) = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_np_expanded})

    boxes_m = np.squeeze(boxes)
    classes_m = np.squeeze(classes).astype(np.int32)
    scores_m = np.squeeze(scores)


    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=4)

    object_detected = detect_gaze(boxes_m,classes_m,scores_m,norm_pos, height, width)
    
    return image_np, object_detected

def detect_gaze(boxes_m,classes_m, scores_m, norm_pos, height, width):

    posx = norm_pos[0]*width
    posy = norm_pos[1]*height

    detect = []

    ymin, xmin, ymax, xmax = [],[],[],[]
    for i in range(min(5,boxes_m.shape[0])):
        if scores_m[i] > 0.5:
            if classes_m[i] in category_index.keys():
                detect.append(category_index[classes_m[i]]['name'])
                ymin.append(int(boxes_m[i][0]*height))
                xmin.append(int(boxes_m[i][1]*width))
                ymax.append(int(boxes_m[i][2]*height))
                xmax.append(int(boxes_m[i][3]*width))

    index = None
    #ymin, xmin, ymax, xmax = boxes_detect
    for i in range(len(detect)):
        if((ymin[i]<posy<ymax[i]) and (xmin[i] < posx < xmax[i])):
            print("objeto apuntado: ", detect[i])
            index = i
            break
    object_detected = None
    if detect is not None and index is not None:
        print("Se ha detectado que la fijacion ({}, {}) apunta al objeto {}".format(posx, posy,detect[index]))
        object_detected = detect[index]

    return object_detected



def worker(input_q, output_q):
    # Load a (frozen) Tensorflow model into memory.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
        sess = tf.Session(graph=detection_graph)

    fps = FPS().start()
    while True:
        fps.update()
        frame = input_q.get()
        height, width, depth = frame[0].shape

        if len(frame) == 2:
            frame_rgb = cv2.cvtColor(frame[0], cv2.COLOR_BGR2RGB)
            output_q.put(detect_objects(frame_rgb, sess, detection_graph, frame[1], height, width))
        # Check frame object is a 2-D array (video) or 1-D (webcam)
        # if len(frame) == 2:
        #     frame_rgb = cv2.cvtColor(frame[1], cv2.COLOR_BGR2RGB)
        #     output_q.put((frame[0], detect_objects(frame_rgb, sess, detection_graph)))
        # else:
        #     frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #     output_q.put(detect_objects(frame_rgb, sess, detection_graph))
    fps.stop()
    sess.close()
