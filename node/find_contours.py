#!/usr/bin/env python

""" find_contours.py

A ROS node to find contours from image topic.
"""

import rospy
import sys
import cv2

from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge, CvBridgeError
import numpy as np

class FindContoursNode():
    def __init__(self):
        self.node_name = "find_contours"
        
        rospy.init_node(self.node_name)
        
        # What we do during shutdown
        rospy.on_shutdown(self.cleanup)
        
        # Create the OpenCV display window for the RGB image
        self.cv_window_name = self.node_name
        cv2.namedWindow(self.cv_window_name, cv2.CV_WINDOW_AUTOSIZE)
        cv2.moveWindow(self.cv_window_name, 25, 75)
        
        # Create the cv_bridge object
        self.bridge = CvBridge()
        
        # Subscribe to the camera image and depth topics and set
        # the appropriate callbacks
        self.image_sub = rospy.Subscriber("/image", Image, self.image_callback)
        
        rospy.loginfo("Waiting for image topics...")

    def image_callback(self, ros_image):
        # Use cv_bridge() to convert the ROS image to OpenCV format
        try:
            frame = self.bridge.imgmsg_to_cv(ros_image, "bgr8")
        except CvBridgeError, e:
            print e
        
        # Convert the image to a Numpy array since most cv2 functions
        # require Numpy arrays.
        frame = np.array(frame, dtype=np.uint8)
        
        # Process the frame using the process_image() function
        display_image = self.process_image(frame)
                       
        # Display the image.
        cv2.imshow(self.node_name, display_image)
        
        # Process any keyboard commands
        self.keystroke = cv2.waitKey(5)
        if 32 <= self.keystroke and self.keystroke < 128:
            cc = chr(self.keystroke).lower()
            if cc == 'q':
                # The user has press the q key, so exit
                rospy.signal_shutdown("User hit q key to quit.")
                
    def process_image(self, frame):
        # Convert to greyscale
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Blur the image
        grey = cv2.blur(grey, (7, 7))
        
        # Compute edges using the Canny edge filter
        edges = cv2.Canny(grey, 30.0, 100.0)

        # Create contorus
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL,\
                                                   cv2.CHAIN_APPROX_SIMPLE)
        
        # draw
        cv2.drawContours(frame ,contours, -1, (0,255,0), 0)

        print "contour size = " + str(len(contours))
        return edges
    
    def cleanup(self):
        print "Shutting down vision node."
        cv2.destroyAllWindows()   

def main(args):       
    try:
        FindContoursNode()
        rospy.spin()
    except KeyboardInterrupt:
        print "Shutting down vision node."
        cv.DestroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)
    
