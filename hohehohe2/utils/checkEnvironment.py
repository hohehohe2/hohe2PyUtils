# -*- coding: utf-8 -*-

"""
GUI環境かどうか、Maya環境かどうかなどのチェックを行う。
"""

def isGuiEnvironment():
	"""
	PySideによるGUI環境下にあればTrueを返す。
	"""
	try:
		from PySide import QtGui
		return bool(QtGui.QApplication.instance())
	except:
		return False

def isMayaEnvironment():
	"""
	Maya環境下にあればTrueを返す。
	"""
	try:
		import maya.cmds
		return True
	except:
		return False
