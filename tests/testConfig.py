# -*- coding: utf-8 -*-

import os, unittest, inspect
from hohehohe2.utils.config import Config


#============================================================================
#============================================================================
class TestConfig(unittest.TestCase):

	def setUp(self):
		configFilePath = os.path.join(self._getThisDirPath(), 'config/config.txt')
		self.config = Config(configFilePath)

	def tearDown(self):
		pass

	def testRead(self):
		self.assertEqual(self.config.get('b'), 2)
		self.assertEqual(self.config.get('c'), 'some text')

	def testOverride(self):
		self.assertEqual(self.config.get('a'), 10)

	def _getThisDirPath(self):
		"""
		このテストファイルのあるディレクトリを返す。
		"""
		return os.path.dirname(inspect.getabsfile(TestConfig))


#============================================================================
#============================================================================
if __name__ == "__main__":
	unittest.main()
