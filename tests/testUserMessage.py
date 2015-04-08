# -*- coding: utf-8 -*-

import sys, unittest
from hohehohe2.utils.userMessage import showInfo, showWarning, showError


#============================================================================
#============================================================================
class TestUserMessage(unittest.TestCase):

	def testShowInfo(self):
		showInfo('info')

	def testShowWarning(self):
		showWarning('warning')

	def testShowError(self):
		showError('error')


#============================================================================
#============================================================================
if __name__ == "__main__":
	#Console mode.
	showInfo('info')
	showWarning('warning')
	showError('error')

	#GUI mode.
	global app
	from PySide import QtGui
	app = QtGui.QApplication(sys.argv)
	unittest.main()
	app.exec_()
