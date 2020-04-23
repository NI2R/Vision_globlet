#!/usr/bin/env python


import sys
import os
import cv2
import numpy as np;


from interfaceROS import Robot_properties
from  cv_bridge import CvBridge
 
class Tester:
	def __init__(self):
		self.robot = Robot_properties() #Objet contenant les infos du sub et sub (interface ROS et ici l'image IN et la position OUT
		self.moyenne = np.zeros((50,720), dtype=float)
		self.traitement = 4 
		self.index = 0

	def updater(self):
		#self.displayImage(self.robot.imageBrut)
		#self.outputROSImage(self.robot.imageBrut)
		self.getBlob(self.robot.imageBrut)
	
	def displayImage(self, image_message):#permet d'afficher une image provenant de ROS dans OpenCV
		bridge = CvBridge()
		cv_image = bridge.imgmsg_to_cv2(image_message, desired_encoding='passthrough')
		cv2.imshow('image',cv_image)
		cv2.waitKey(0)
		cv2.destroyAllWindows()


	def outputROSImage( self, image_message):#permet d'afficher une image provenant de ROS passant dans OpenCV et republie dans ROS
		bridge = CvBridge()
		cv_image = bridge.imgmsg_to_cv2(image_message, desired_encoding='passthrough')
		image_ROS = bridge.cv2_to_imgmsg(cv_image, encoding="passthrough")
		self.robot.publishImage(image_ROS) 

	def outputOpenCVImage( self, cv_image):#permet d'afficher une image provenant de OpenCV et publier dans ROS
		bridge = CvBridge()
		image_ROS = bridge.cv2_to_imgmsg(cv_image, encoding="passthrough")
		self.robot.publishImage(image_ROS) 

	def getBlob(self, image_message):
		bridge = CvBridge()
		cv_image = bridge.imgmsg_to_cv2(image_message, desired_encoding="bgr8")

		#cv_image = cv_image[:,:,1]#permet de recuperer seulement une couleur : cv_image[:,:,0] cv_image[:,:,1] cv_image[:,:,2]
		#cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY) #convertit une image couleur en image niveau de gris.		
		
		#Application d'un filtre laplacien ici sur une composante :
		#cv_image = cv2.split(cv_image)[2]
		#cv_image = cv2.Laplacian(cv_image, cv2.CV_8U, ksize = 3)
		
		#tester erode pour filtrer puis dilater et ca retire le bruit
		
		#Detection des aretes par l'algorithme de Canny :
		#cv_image = cv_image[:,:,2]

		cv_image = cv_image[500:550,280:1000]
		cv_image = cv2.Canny(cv_image, 50, 200) 
		for i in range(0,50):
   			for j in range(0,720):
            			self.moyenne[i,j] = cv_image[i,j] + self.moyenne[i,j]
		


		if self.index == self.traitement:
			for i in range(0,50):
   				for j in range(0,720):
					self.moyenne[i,j] = self.moyenne[i,j]/(self.traitement+1)
					
					if self.moyenne[i,j] > 150:
            					cv_image[i,j] = 255
					else:
						cv_image[i,j] = 1

			
			self.index = 0
			self.moyenne = self.moyenne * 0
			self.outputOpenCVImage(cv_image)

		else:
			
			self.index = self.index + 1

	
		#cv_image[1,1] = np.array([0,0,0])

		#for i in range(0,250):
   		#	for j in range(0,640):
            	#		cv_image[i,j] = 1
		

		#for i in range(400,480):
   		#	for j in range(0,640):
            	#		cv_image[i,j] = 1











		# Setup SimpleBlobDetector parameters.
		#params = cv2.SimpleBlobDetector_Params()

		# Change thresholds
		#params.minThreshold = 100
		#params.maxThreshold = 1000

		# Filter by Area.
		#params.filterByArea = False
		#params.minArea = 150

		# Filter by Circularity
		#params.filterByCircularity = True
		#params.minCircularity = 0.05#0.1

		# Filter by Convexity
		#params.filterByConvexity = True
		#params.minConvexity = 0.5	#0.87

		# Filter by Inertia
		#params.filterByInertia = True
		#params.minInertiaRatio = 0.01

		# Set up the detector with default parameters.
		#detector = cv2.SimpleBlobDetector_create(params)

		# Detect blobs.
		#keypoints = detector.detect(cv_image)

		# Draw detected blobs as red circles.
		# cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
		#im_with_keypoints = cv2.drawKeypoints(cv_image, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)



		# Show keypoints
		#cv2.imshow("Keypoints", im_with_keypoints)
		#cv2.waitKey(0)








