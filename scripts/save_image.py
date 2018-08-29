#! /usr/bin/python

import rospy
import cv2
from sensor_msgs.msg import Image
import os
import time
from cv_bridge import CvBridge

camera_image = None
image_updated = False
_cv_bridge = CvBridge()

def image_callback(img):
  global camera_image
  camera_image  = img
  global image_updated
  image_updated = True

if __name__ == "__main__":
  node_name = "save_image"
  rospy.init_node(node_name)
  sub_image_topic = rospy.get_param("~sub_image_topic", "/camera/image_raw")
  image_saved_path = rospy.get_param("~image_saved_path", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'output_images'))
  
  image_sub = rospy.Subscriber(sub_image_topic, Image, image_callback, queue_size=1)
  
  rospy.loginfo('''Press key "s" on image for save image''')
  image_index = 0
  pre_date_time = None

  while not rospy.is_shutdown():
    if image_updated:
      cv_image = _cv_bridge.imgmsg_to_cv2(camera_image)
      cv2.imshow("image", cv_image)
      key_num = cv2.waitKey(100) & 0xFF
      if key_num == 27:
        rospy.loginfo("exist " + node_name + " node")
        cv2.destroyAllWindows()
        break
      elif chr(key_num) == "s":
        date_time = time.strftime("%Y%m%d_%H%M%S")
        
        if pre_date_time == date_time:
          image_index += 1
          suffix = "_%d" % image_index 
          image_name = "img_" + date_time + suffix + ".png"
        else:
          pre_date_time = date_time
          image_index = 0
          image_name = "img_" + date_time + ".png"
        
        cv2.imwrite(image_saved_path+"/"+image_name, cv_image)
        rospy.loginfo("Saved one image " + image_name + " in: " +image_saved_path)
        image_updated = False
  
  rospy.spin()
