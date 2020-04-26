#!/usr/bin/env python

#permet de convertir des variable de type ROS en variable que je vais utiliser
	#Subscriber(nom topic, type variable topic, fonction appele lors d'une maj)
	#self.pub = rospy.Publisher(nom topic, type variable topic, queue_size=1 par defaut)


import sys
import os
import rospy

import traiteImage

from std_msgs.msg import String as ROS_String
from sensor_msgs.msg import Image as ROS_Image
from geometry_msgs.msg import Pose as ROS_Pose


class Robot_properties:
	def __init__(self):

		self.imageBrut = ROS_Image()

		self.publish_topic = 'positionGoblet' #nom du topic que je publie
		self.publish_topic_Img = 'imgGoblet'
		
		self.subscribe_topic = 'CamGoblet/image_raw' #nom du topic que je veux recuperer

		self.pub = rospy.Publisher(self.publish_topic, ROS_Pose, queue_size=1)
		self.pubImg = rospy.Publisher(self.publish_topic_Img, ROS_Image, queue_size=1)
		
		rospy.Subscriber(self.subscribe_topic, ROS_Image, self.subscrib) 

	def subscrib(self, ros_data):
		self.imageBrut = ros_data #on recupere l'image complet

	def publish(self, posX, posY): #x sera la position et y la couleur
		Msg = ROS_Pose()
		Msg.position.x = posX #pb car ici attend float mais nous lui donnons un byte				
		Msg.position.y = posY #pb car ici attend float mais nous lui donnons un byte
		self.pub.publish(Msg)

	def publishImage(self, image):
		self.pubImg.publish(image)



def main():
	rospy.init_node('Traite_Image', anonymous=True)
	Objtester = traiteImage.Tester() #objet de type objet
	rospy.sleep(5)
	while not rospy.is_shutdown():
		Objtester.updater()
		rospy.sleep(0.03)


if __name__ ==  '__main__':
	try:
		main()
	except rospy.ROSInterruptException:
		pass
