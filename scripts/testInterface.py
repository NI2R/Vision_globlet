#!/usr/bin/env python

import sys
import os
from interfaceROS import Robot_properties

class Tester:
	def __init__(self):
		self.my_message = "Hello world!"
		self.robot = Robot_properties()

	def updater(self):
		print(self.robot.messageIn)
		self.robot.publish(self.my_message)
