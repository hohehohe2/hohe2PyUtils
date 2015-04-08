# -*- coding: utf-8 -*-

"""
ユーザーに対しメッセージを送るモジュール。
GUIモードとGUIのないモード、Maya内で実行されるかどうかなどに応じて挙動が異なる。
"""

from hohehohe2.utils.checkEnvironment import isGuiEnvironment, isMayaEnvironment

def showInfo(msg):
	"""
	Info表示。msgが日本語ならunicode文字列であること。
	"""
	print msg
	if isGuiEnvironment():
		from PySide import QtGui
		QtGui.QMessageBox.information(None, 'Info', msg)

def showWarning(msg):
	"""
	Warning表示。msgが日本語ならunicode文字列であること。
	"""
	if isMayaEnvironment():
		import maya.cmds as cmds
		cmds.warning(msg)
	else:
		print msg

	if isGuiEnvironment():
		from PySide import QtGui
		QtGui.QMessageBox.warning(None, 'Warning', msg)

def showError(msg):
	"""
	Error表示。msgが日本語ならunicode文字列であること。
	"""
	if isMayaEnvironment():
		import maya.OpenMaya as om
		om.MGlobal.displayError(msg)
	else:
		print msg

	if isGuiEnvironment():
		from PySide import QtGui
		QtGui.QMessageBox.critical(None, 'Error', msg)
