# -*- coding: utf-8 -*-

import os, unittest, inspect
from hohehohe2.utils.pluginReader import PluginReader
from hohehohe2.utils.myException import MyException


#============================================================================
#============================================================================
class TestPluginReaderBase(unittest.TestCase):

	def _getThisDirPath(self):
		"""
		このテストファイルのあるディレクトリを返す。
		"""
		return os.path.dirname(inspect.getabsfile(TestPluginReaderBase))


#============================================================================
#============================================================================
class TestPluginReader(TestPluginReaderBase):

	def setUp(self):
		pluginDirPath = os.path.join(self._getThisDirPath(), 'plugins')
		self.reader = PluginReader(pluginDirPath)

	def testLoad(self):
		plugin = self.reader.get('testPlugin')
		self.assertEqual(plugin.a, 'py file plugin')

	def testPycLoad(self):
		plugin = self.reader.get('testPycPlugin')
		self.assertEqual(plugin.a, 'py file deleted')

	def testNonExistPluginFail(self):
		self.assertRaises(MyException, lambda: self.reader.get('tako'))


#============================================================================
#============================================================================
class TestPluginReaderWithDefault(TestPluginReaderBase):

	def setUp(self):
		pluginDirPath = os.path.join(self._getThisDirPath(), 'plugins')
		self.reader = PluginReader(pluginDirPath, 'default')

	def testDefault(self):
		plugin = self.reader.get('tako')
		self.assertEqual(plugin.__name__, 'default')
		self.assertEqual(plugin.a, 'default plugin')


#============================================================================
#============================================================================
class TestPluginReaderWithNonExistDefault(TestPluginReaderBase):

	def setUp(self):
		pluginDirPath = os.path.join(self._getThisDirPath(), 'plugins')
		self.reader = PluginReader(pluginDirPath, 'ika')

	def testNonExistDefaultPluginFail(self):
		self.assertRaises(MyException, lambda: self.reader.get('tako'))


#============================================================================
#============================================================================
if __name__ == "__main__":
	unittest.main()
