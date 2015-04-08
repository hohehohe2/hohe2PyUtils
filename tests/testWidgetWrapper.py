# -*- coding: utf-8 -*-

import os, sys, unittest

from PySide import QtCore, QtGui
from PySide.QtUiTools import QUiLoader
from hohehohe2.utils.widgetWrappers import *


#============================================================================
#============================================================================
class MyMainWindow(QtGui.QMainWindow):

	def __init__(self, tester):

		super(MyMainWindow, self).__init__(None)
		loader = QUiLoader()
		currentPath = os.path.dirname(__file__)
		uiFilePath = os.path.join(currentPath, 'uiFiles', 'wrapperExample.ui')
		self.ui = loader.load(uiFilePath)
		convertUiWidgets(self.ui)
		self.setCentralWidget(self.ui)

		self.ui.myLabel3.mySet('tako')
		tester.assertEqual(self.ui.myLabel3.myGet(), 'tako')

		self.ui.myButton.mySet('tako')
		tester.assertEqual(self.ui.myButton.myGet(), 'tako')
		self.ui.myButton.myConnect(self.__slot)

		self.ui.myCheckBox.mySet(True)
		tester.assertEqual(self.ui.myCheckBox.myGet(), True)
		self.ui.myCheckBox.mySet(False)
		tester.assertEqual(self.ui.myCheckBox.myGet(), False)
		self.ui.myCheckBox.mySet(QtCore.Qt.PartiallyChecked)
		tester.assertEqual(self.ui.myCheckBox.myGet(), QtCore.Qt.CheckState.PartiallyChecked)
		self.ui.myCheckBox.myConnect(self.__slot)
		self.ui.myCheckBox.myClearSelection()

		self.ui.myComboBox.mySet('tako')
		tester.assertEqual(self.ui.myComboBox.myGet(), 'tako')
		self.ui.myComboBox.myConnect(self.__slot)
		self.ui.myComboBox.myAdd('hitode')
		self.ui.myComboBox.myRemove('ika')
		self.ui.myComboBox.myClear()

		self.ui.mySpinBox.mySet(3)
		tester.assertEqual(self.ui.mySpinBox.myGet(), 3)
		self.ui.mySpinBox.myConnect(self.__slot)

		self.ui.myDoubleSpinBox.mySet(3)
		tester.assertEqual(self.ui.myDoubleSpinBox.myGet(), 3.0)
		self.ui.myDoubleSpinBox.myConnect(self.__slot)

		self.ui.myLineEdit.mySet('tako')
		tester.assertEqual(self.ui.myLineEdit.myGet(), 'tako')
		self.ui.myLineEdit.myConnect(self.__slot)

		self.ui.myTextEdit.mySet('tako')
		tester.assertEqual(self.ui.myTextEdit.myGet(), 'tako')
		self.ui.myTextEdit.myConnect(self.__slot)

		self.ui.myHorizontalSlider.mySet(33)
		tester.assertEqual(self.ui.myHorizontalSlider.myGet(), 33)
		self.ui.myHorizontalSlider.myConnect(self.__slot)

		self.ui.myVerticalSlider.mySet(33)
		tester.assertEqual(self.ui.myVerticalSlider.myGet(), 33)
		self.ui.myVerticalSlider.myConnect(self.__slot)

		self.ui.myRadioButton1.mySet(True)
		tester.assertEqual(self.ui.myRadioButton1.myGet(), True)
		self.ui.myRadioButton1.myConnect(self.__slot)
		self.ui.myRadioButton1.myClearSelection()

		self.ui.myTreeWidget.mySelect('tako')
		self.ui.myTreeWidget.mySelectList(['ika', 'kani'])
		tester.assertEqual(self.ui.myTreeWidget.myGet(), 'kani')
		tester.assertEqual(self.ui.myTreeWidget.myGetList(), ['ika', 'ika', 'kani'])
		self.ui.myTreeWidget.myConnect(self.__slot)
		self.ui.myTreeWidget.myClearSelection()
		self.ui.myTreeWidget.myClear()


		self.ui.myTableWidget.mySelect('tako')
		self.ui.myTableWidget.mySelectList(['ika', 'kani'])
		tester.assertEqual(self.ui.myTableWidget.myGet(), 'kani')
		tester.assertEqual(self.ui.myTableWidget.myGetList(), ['ika', 'ika', 'kani'])
		tester.assertEqual(self.ui.myTableWidget.myGet('uni', 'ebi'), 'uniebi')
		uniebiText = self.ui.myTableWidget.myGet('uni', 'ebi')
		self.ui.myTableWidget.mySet('uni', 'ebi', uniebiText + ' dayo')
		tester.assertEqual(self.ui.myTableWidget.myGet(1, 0), 'uniebi dayo')
		self.ui.myTableWidget.myConnect(self.__slot)
		self.ui.myTableWidget.myClearSelection()
		self.ui.myTableWidget.myClear()

	def __slot(self, *args, **kargs):
		print args, kargs


class TestFileLock(unittest.TestCase):

	def testMain(self):
		app = QtGui.QApplication(sys.argv)
		ui = MyMainWindow(self)
		ui.show()
		app.exec_()


if __name__ == '__main__':
	unittest.main()
