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

		#Val TraitMano
		self.moyenne = np.zeros((50,720), dtype=float) #matrice qui me sert pour faire la moyenne de plusieurs images (TraitMano)
		self.traitement = 4 #Nombre d'image que j'utilise pour realiser une moyenne dans TraitImage.
		self.index = 0
		#######################

		#val definit pour dimensionner ma zone de travail
		self.bDroit = 1000
		self.bGauche = 280
		self.bHaut = 475
		self.bBas = 525

		self.hauteur = self.bBas - self.bHaut
		self.largeur = self.bDroit - self.bGauche

		self.bord1 = -999
		self.bord2 = -999
		self.couleurGob = -1

	def updater(self):
		#self.displayImage(self.robot.imageBrut)
		#self.outputROSImage(self.robot.imageBrut)
		#self.getBlob(self.robot.imageBrut)
		#self.traitMano(self.robot.imageBrut)#Exemple fonctionnel mais traitement long
		self.traitFiltre(self.robot.imageBrut)#Exemple fonctionnel mais traitement long
		
	
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
	
	def outputPosiAndColor(self, posi, color):
		self.robot.publish(posi, color) 
	

	def traitFiltre(self, image_message):
		bridge = CvBridge()
		cv_image = bridge.imgmsg_to_cv2(image_message, desired_encoding="bgr8")

		cv_image = cv_image[self.bHaut:self.bBas,self.bGauche:self.bDroit]#je recadre l'image pour ne prendre que l'essentiel
		cv_imageCLRGoblet = cv_image

		#J'errode ici
		kernel = np.ones((5,5),np.uint8)
		cv_image = cv2.erode(cv_image,kernel,iterations = 1)
		cv_image = cv2.erode(cv_image,kernel,iterations = 1)
		cv_image = cv2.erode(cv_image,kernel,iterations = 1)
		cv_image = cv2.erode(cv_image,kernel,iterations = 1)
		#cv_image = cv2.erode(cv_image,kernel,iterations = 1)#

		#je dilate ensuite 
		#cv_image = cv2.dilate(cv_image,kernel,iterations = 1)
	
		#j'applique opening (errode suivit d'un dilate)
		cv_image = cv2.morphologyEx(cv_image, cv2.MORPH_OPEN, kernel)

		cv_image = cv2.dilate(cv_image,kernel,iterations = 1)
		#cv_image = cv2.dilate(cv_image,kernel,iterations = 1)#
		
		#Puis j'applique Canny
		cv_image = cv2.Canny(cv_image, 50, 200) 

		#self.outputOpenCVImage(cv_image)
		self.transformPix(cv_image)#On appel la fonction dessous

		print str(self.bord1) + '     ' + str(self.bord2)

		########Partie pour trouver la couleur dominante qui se trouve a gauche du bord1
		cv_imageCLRGoblet = cv_imageCLRGoblet[:,self.bord2 - 230 - 50:self.bord2 - 230 + 50]

		averageColor = cv2.mean(cv_imageCLRGoblet)

		if averageColor[1] > averageColor[2]:	#couleur majoritaire est VERT
			self.couleurGob = 1
			print "vert    : "+ str(self.couleurGob)
		elif averageColor[2] > averageColor[1]:	#couleur majoritaire est ROUGE
			self.couleurGob = 2
			print "rouge     : " + str(self.couleurGob)
	
		#Renvoyer ici le self.bord2 + la couleur du gobelet
		self.outputPosiAndColor(self.bord2, self.couleurGob)
		self.outputOpenCVImage(cv_imageCLRGoblet)

	def transformPix(self, image_message):
		
		cv_image = image_message
		
		#self.outputOpenCVImage(cv_image)
		
		# traiterment pour obtenir que des barres vertical(je met la colonne en blanc des que 1 pixel de la colonne est blanc)
		for i in range(0,self.largeur-1):
   				for j in range(0,self.hauteur):
					if cv_image[j,i] == 255:
						#la on modifie la ligne entiere  a 255
						for k in range(0, self.hauteur):
							cv_image[k,i] = 255
						if i < self.largeur-1: 
							i = i + 1
							j = 0	

		#self.outputOpenCVImage(cv_image)		
		
		cv_image = cv_image[0:1,:]#je recadre l'image pour ne prendre que l'essentiel
		lastPixel = 0
		for j in range(0,self.largeur):
			if cv_image[0,j] == 255:
				if j - lastPixel < 50:
					for i in range(lastPixel,j):
		#				for k in range(0,self.hauteur):
							cv_image[0,i] = 255
				lastPixel = j
				

		#self.outputOpenCVImage(cv_image)
		self.getCoordo(cv_image)


	def getCoordo(self, image_message):

		cv_image = image_message
		self.bord1 = -1
		self.bord2 = -1
		
		x1bord1 = -1
		x2bord1 = -1
		
		x1bord2 = -1
		x2bord2 = -1
		
		i = self.largeur-1
		valpreced = 0

		while i > 0 :
			if cv_image[0,i] == 255 and valpreced == 0: 
				if x2bord2 == -1 : 
					x2bord2 = i
				elif x2bord1 == -1 : 
					x2bord1 = i
			if cv_image[0,i] == 0 and valpreced == 255: 
				if x1bord2 == -1 :
					x1bord2 = i
				elif x2bord1 == -1 : 
					x2bord1 = i

			
			valpreced = cv_image[0,i]
			i = i - 1

		dif2 = x2bord2 - x1bord2
		self.bord2 = x2bord2 - (dif2/2)

		if x2bord1 > -1:		

			if x1bord1 == -1:
				self.bord1 = x2bord1 - (dif2/2)

			else :
				dif1 = x2bord1 - x1bord1
				self.bord1 = x2bord1 - (dif1/2)

		else :
			self.bord1 = -999


		#print str(self.bord1) + '     ' + str(self.bord2)

	














	def traitMano(self, image_message):

		bridge = CvBridge()
		cv_image = bridge.imgmsg_to_cv2(image_message, desired_encoding="bgr8")

		cv_image = cv_image[500:550,280:1000]#je recadre l'image pour ne prendre que l'essentiel
		
		#Detection des aretes par l'algorithme de Canny :

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
			self.outputOpenCVImage(cv_image) #je out ici
		else:
			self.index = self.index + 1


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





