# -*- coding: utf-8 -*-

"""
mySet() : 値のセット。
myGet() : 値の取得。

mySelect() : 値の選択。
myClearSelection(): 値の全選択解除。

myAdd() : 値の追加。
myRemove() : 値の削除。
myClear() : 値の全削除。

myConnect() : signal-slotコネクト。

複数のデータを扱うものは上記メソッド名の最後にListがつく、mySetList()など。
"""

import os, sys, logging
from PySide import QtCore, QtGui


#============================================================================
#============================================================================
class _MyWidget(object):

	def __init__(self, widget):
		self.widget = widget

	def __getattr__(self, name):
		return getattr(self.widget, name)


#============================================================================
#============================================================================
class MyQLabel(_MyWidget):

	def myGet(self):
		return self.widget.text()

	def mySet(self, text):
		self.widget.setText(text)


#============================================================================
#============================================================================
class _MyQAbstractPushButton(_MyWidget):

	def myGet(self):
		return self.widget.text()

	def mySet(self, text):
		self.widget.setText(text)


#============================================================================
#============================================================================
class MyQPushButton(_MyQAbstractPushButton):

	def myConnect(self, *args, **kargs):
		self.widget.clicked.connect(*args, **kargs)


#============================================================================
#============================================================================
class MyQCheckBox(_MyQAbstractPushButton):

	def myGet(self):
		val = self.widget.checkState()
		return {
			QtCore.Qt.Unchecked : False,
			QtCore.Qt.PartiallyChecked : QtCore.Qt.PartiallyChecked,
			QtCore.Qt.Checked : True
			}[val]

	def mySet(self, trueOrFalseOrPartially):
		val = {
			False : QtCore.Qt.Unchecked,
			QtCore.Qt.PartiallyChecked : QtCore.Qt.PartiallyChecked,
			True : QtCore.Qt.Checked
			}[trueOrFalseOrPartially]
		self.widget.setCheckState(val)

	def mySelect(self, trueOrFalseOrPartially):
		self.mySet(trueOrFalseOrPartially)

	def myClearSelection(self):
		self.mySet(False)

	def myConnect(self, *args, **kargs):
		self.widget.stateChanged.connect(*args, **kargs)


#============================================================================
#============================================================================
class MyQRadioButton(_MyQAbstractPushButton):

	def myGet(self):
		return self.widget.isChecked()

	def mySet(self, trueOrFalse):
		self.widget.setChecked(trueOrFalse)

	def mySelect(self,trueOrFalse):
		self.mySet(trueOrFalse)

	def myClearSelection(self):
		self.mySelect(False)

	def myConnect(self, *args, **kargs):
		self.widget.toggled.connect(*args, **kargs)


#============================================================================
#============================================================================
class MyQComboBox(_MyWidget):

	def myGet(self):
		return self.widget.currentText()

	def mySet(self, text):
		self.mySelect(text)

	def mySelect(self, text):
		index = self.widget.findText(text)
		if index != -1:
			self.widget.setCurrentIndex(index)

	def myAdd(self, text):
		self.widget.addItem(text)

	def myRemove(self, text):
		index = self.widget.findText(text)
		if index != -1:
			self.widget.removeItem(index)

	def myClear(self):
		self.widget.clear()

	def myConnect(self, *args, **kargs):
		self.widget.currentIndexChanged.connect(*args, **kargs)


#============================================================================
#============================================================================
class _MyAbstractQSpinBox(_MyWidget):

	def myGet(self):
		return self.widget.value()

	def mySet(self, value):
		self.widget.setValue(value)

	def myConnect(self, *args, **kargs):
		self.widget.valueChanged.connect(*args, **kargs)


#============================================================================
#============================================================================
class MyQSpinBox(_MyAbstractQSpinBox):
	pass


#============================================================================
#============================================================================
class MyQDoubleSpinBox(_MyAbstractQSpinBox):
	pass


#============================================================================
#============================================================================
class MyQLineEdit(_MyWidget):

	def myGet(self):
		return self.widget.text()

	def mySet(self, text):
		self.widget.setText(text)

	def myClear(self):
		self.mySet('')

	def myConnect(self, *args, **kargs):
		self.widget.textEdited.connect(*args, **kargs)


#============================================================================
#============================================================================
class MyQTextEdit(_MyWidget):

	def myGet(self):
		return self.widget.toPlainText()

	def mySet(self, text):
		self.widget.setPlainText(text)

	def myClear(self):
		self.mySet('')

	def myConnect(self, *args, **kargs):
		self.widget.textChanged.connect(*args, **kargs)


#============================================================================
#============================================================================
class _MyAbstractQSlider(_MyWidget):

	def myGet(self):
		return self.widget.value()

	def mySet(self, value):
		self.widget.setValue(value)

	def myConnect(self, *args, **kargs):
		self.widget.valueChanged.connect(*args, **kargs)


#============================================================================
#============================================================================
class MyQSlider(_MyAbstractQSlider):
	pass


#============================================================================
#============================================================================
class _MyQTreeTableWidgetBase(_MyWidget):

	def myClearSelection(self):
		self.widget.selectionModel().setCurrentIndex(QtCore.QModelIndex(), QtGui.QItemSelectionModel.Clear)

	def _selectListAndMakeCurrent(self, items):
		#最後のitemをCurrentにする。
		if items:
			self.widget.setCurrentItem(items[-1])

		#Selectする.
		sModel = self.widget.selectionModel()
		for item in items:
			index = self.widget.indexFromItem(item)
			sModel.select(index, QtGui.QItemSelectionModel.Select)


#============================================================================
#============================================================================
#selectとcurrentの違いに注意すること。
#QTreeWidgetではItemは行を表す。各行にはカラムと子itemがある。
class MyQTreeWidget(_MyQTreeTableWidgetBase):

	def myGet(self):
		item = self.widget.currentItem()
		if item:
			return item.text(0)

	def myGetList(self):
		items = self.widget.selectedItems()
		return [x.text(0) for x in items]

	def mySelect(self, text):
		self.myClearSelection()
		items = self.widget.findItems(text, QtCore.Qt.MatchFixedString|QtCore.Qt.MatchCaseSensitive)
		if items:
			self.widget.scrollTo(self.widget.indexFromItem(items[0]))
			self.widget.setCurrentItem(items[0]) #selectし、カレントにもする。

	def mySelectList(self, texts):
		self.myClearSelection()

		if isinstance(texts, basestring):
			texts = [texts]

		items = []
		for text in texts:
			items.extend(self.widget.findItems(text, QtCore.Qt.MatchFixedString|QtCore.Qt.MatchCaseSensitive))

		self._selectListAndMakeCurrent(items)

	def mySet(self, text):
		self.mySelect(text)

	def mySetList(self, texts):
		self.mySelectList(texts)

	def myAdd(self, text):
		raise NotImplementedError('To be implemented.')

	def myRemove(self, text):
		raise NotImplementedError('To be implemented.')

	def myClear(self):
		self.widget.clear()

	def myConnect(self, *args, **kargs):
		if self.widget.selectionMode() == QtGui.QAbstractItemView.SingleSelection:
			self.widget.currentItemChanged.connect(*args, **kargs)
		else:
			self.widget.itemSelectionChanged.connect(*args, **kargs)


#============================================================================
#============================================================================
#selectとcurrentの違いに注意すること。
#QTableWidgetではItemはセルを表す。
class MyQTableWidget(_MyQTreeTableWidgetBase):

	def myGet(self, *args):
		"""
		引数について。
		引数なし：currentの文字列を返す。
		row, column：row, columnで指定されたセルの文字列を返す。
		"""
		if len(args) == 0:
			item = self.widget.currentItem()
			if item:
				return item.text()
		elif len(args) == 2:
			row, column = self.__getRowColumnIndexes(args[0], args[1])
			item = self.widget.item(row, column)
			if item:
				return item.text()
		else:
			raise Exception('Number of myGet params must be 0 or 2, got %d' % len(args))

	def myGetList(self):
		items = self.widget.selectedItems()
		return [x.text() for x in items]

	def mySelect(self, *args):
		"""
		引数について。
		文字列：その文字列のあるセルを1つだけ選択する。
		row, column：row, columnで指定されたセルを選択する。columnとrowはindexか、あるいはヘッダ文字列で指定する。
		"""
		self.myClearSelection()
		items = []
		self.__getItems(items, *args)
		if items:
			self.widget.setCurrentItem(items[0])

	def mySelectList(self, *args):
		"""
		引数について。
		文字列：その文字列のあるセルを選択する。
		row, column：row, columnで指定されたセルを選択する。columnとrowはindexか、あるいはヘッダ文字列で指定する。
		複数指定時にはこの2つの指定方法ととったときのパラメータをタプルで渡す。
		"""
		self.myClearSelection()
		items = []
		self.__getItems(items, *args)
		self._selectListAndMakeCurrent(items)

	def mySet(self, row, column, text):
		row, column = self.__getRowColumnIndexes(row, column)
		self.widget.item(row, column).setText(text)

	def myAdd(self, text):
		raise NotImplementedError('To be implemented.')

	def myRemove(self, text):
		raise NotImplementedError('To be implemented.')

	def myClear(self):
		self.widget.clear()

	def myConnect(self, *args, **kargs):
		if self.widget.selectionMode() == QtGui.QAbstractItemView.SingleSelection:
			self.widget.currentItemChanged.connect(*args, **kargs)
		else:
			self.widget.itemSelectionChanged.connect(*args, **kargs)

	def __getItems(self, items, *args):

		if len(args) == 1:
			textOrSequence = args[0]
			if isinstance(textOrSequence, basestring):
				#テキストで指定されたので検索。
				foundItems = self.widget.findItems(textOrSequence, QtCore.Qt.MatchFixedString|QtCore.Qt.MatchCaseSensitive)
				items.extend(foundItems)
			else:
				#シーケンス。
				for i in textOrSequence:
					self.__getItems(items, i)

		elif len(args) == 2:
			row, column = args[0], args[1]
			row, column = self.__getRowColumnIndexes(row, column)
			items.append(self.widget.item(row, column))

		else:
			raise Exception('Invalid number of arguments.')

	def __getRowColumnIndexes(self, row, column):
		"""
		row, columnそれぞれについてintまたは文字列を受け取る。
		文字列ならばその文字列をヘッダに持つrow, columnのindexに変換する。
		"""
		if isinstance(row, basestring):
			#ヘッダ文字列でrow指定された。
			for r in range(self.widget.rowCount()):
				if self.widget.verticalHeaderItem(r).text() == row:
					row = r
					break
			else:
				raise Exception('No row which header string is %s found.' % repr(row))

		if isinstance(column, basestring):
			#ヘッダ文字列でcolumn指定された。
			for c in range(self.widget.columnCount()):
				if self.widget.horizontalHeaderItem(c).text() == column:
					column = c
					break
			else:
				raise Exception('No column which header string is %s found.' % repr(column))

		return row, column


#============================================================================
#============================================================================
_wrapperClasses = [c for c in globals().values() if isinstance(c, type) and issubclass(c, _MyWidget) and not c.__name__.startswith('_')]

_myWidgetMap = {}
for wrapperClass in _wrapperClasses:
	name = wrapperClass.__name__[2:] #Remove 'My'.
	_myWidgetMap[name] = wrapperClass

del _wrapperClasses


#============================================================================
#============================================================================
def convertUiWidgets(ui):
	"""
	uiファイルにより生成されたウィジェットが持つ子ウィジェットを自動変換する。
	"""
	for widgetName in dir(ui):
		widget = getattr(ui, widgetName)
		className = widget.__class__.__name__
		if className in _myWidgetMap:
			wrapperClass = _myWidgetMap[className]
			setattr(ui, widgetName, wrapperClass(widget))
