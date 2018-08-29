import sys,os
import yaml
import cv2
import numpy as np
import rospy
import glob

class DistortParam():
  def __init__(self, file):
    self.file = file
    with open(self.file, 'r') as stream:
      skip_lines = 2
      for i in range(skip_lines):
        _ = stream.readline()
      print("escaped the first %d lines..." % skip_lines)
      params = yaml.load(stream)
      self.model_type = params['model_type']
      self.camera_name = params['camera_name']
      self.image_width = params['image_width']
      self.image_height = params['image_height']

      if self.model_type == "MEI":
        self.xi = np.array([[params['mirror_parameters']['xi']]])
        self.K = np.array([
          [params['projection_parameters']['gamma1'], 0.0, params['projection_parameters']['u0']],
          [0.0, params['projection_parameters']['gamma2'], params['projection_parameters']['v0']],
          [0.0, 0.0, 1.0]
        ])
        self.D = np.array([
          [params['distortion_parameters']['k1'],
          params['distortion_parameters']['k2'],
          params['distortion_parameters']['p1'],
          params['distortion_parameters']['p2']]
        ])
      elif self.model_type == "KANNALA_BRANDT" :
        self.K = np.array([
          [params['projection_parameters']['mu'], 0.0, params['projection_parameters']['u0']],
          [0.0, params['projection_parameters']['mv'], params['projection_parameters']['v0']],
          [0.0, 0.0, 1.0]
        ])
        self.D = np.array([
          [params['projection_parameters']['k2'],
          params['projection_parameters']['k3'],
          params['projection_parameters']['k4'],
          params['projection_parameters']['k5']]
        ])
      
if __name__ == '__main__':
  print("openCV Version: %s" % cv2.__version__)
  param_file = '/home/bdai/dataSets/BlueFox/Calibrtion/gopro_test/0_gopro_camera_calib_MEI.yaml'
  param = DistortParam(param_file)
  
  test_data_path = '/home/bdai/dataSets/BlueFox/Calibrtion/gopro_test/'
  files = [file for file in glob.glob(test_data_path+'/*')]
  files.sort()
  Knew = param.K.copy()
  Knew[(0,1), (0,1)] = 0.1*Knew[(0,1), (0,1)]
  w, h = param.image_width, param.image_height
  map1, map2 = cv2.fisheye.initUndistortRectifyMap(param.K, param.D, np.eye(3,3), Knew, (w, h), cv2.CV_16SC2)
  
  for file in files:
    if file.endswith(".bmp") or file.endswith(".jpg"):
      img = cv2.imread(file)
      cv2.imshow('image',img)
      if param.model_type == "MEI":
        undistorted_img	=	cv2.omnidir.undistortImage(
              img, param.K, param.D, param.xi, cv2.omnidir.RECTIFY_PERSPECTIVE, Knew=Knew)
        cv2.imshow('image',img)
        cv2.imshow('undistorted image',undistorted_img)

      elif param.model_type == "KANNALA_BRANDT":
        undistorted_img	=	cv2.fisheye.undistortImage(img, param.K, param.D, Knew=Knew)
        KB_undistorted_img = cv2.remap(img, map1, map2, cv2.INTER_LINEAR, cv2.BORDER_REFLECT)
        # cv2.imshow('undistorted image',undistorted_img)
        cv2.imshow('KB undistorted image',KB_undistorted_img)
      if cv2.waitKey(0) & 0xFF == 27:
        break