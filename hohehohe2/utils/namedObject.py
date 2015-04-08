# -*- coding: utf-8 -*-


#============================================================================
#============================================================================
class NamedObject(object):
	def __init__(self, name):
		self.name = name

	name = 'noname'

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.__class__.__name__ + ":" + self.name
