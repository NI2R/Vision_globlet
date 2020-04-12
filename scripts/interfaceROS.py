#!/usr/bin/env python

import sys
import os
import rospy
import testInterface

from std_msgs.msg import String as ROS_String

class Robot_properties:
	def __init__(self):
		self.messageIn = ""

		self.publish_topic = 'ni2r_test_interface'
		self.subscribe_topic = 'chatter'

		self.pub = rospy.Publisher(self.publish_topic, ROS_String, queue_size=1)
		rospy.Subscriber(self.subscribe_topic, ROS_String, self.subscrib)

	def subscrib(self, ros_data):
		self.messageIn = ros_data

	def publish(self, message):
		self.pub.publish(message)


def main():
	rospy.init_node('Test_interface', anonymous=True)
	tester = testInterface.Tester()
	while not rospy.is_shutdown():
		tester.updater()
		rospy.sleep(1)


if __name__ ==  '__main__':
	try:
		main()
	except rospy.ROSInterruptException:
		pass
