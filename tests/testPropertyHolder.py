# -*- coding: utf-8 -*-

import os, sys, unittest, inspect
from hohehohe2.utils.propertyHolder import PropertyHolder
from hohehohe2.utils.fileLock import FileLock
from hohehohe2.utils.myException import MyException


#============================================================================
#============================================================================
class MyPropertyHolder(PropertyHolder):
	def __init__(self, name, parent, readTimeLimitSec=3.0):
		super(MyPropertyHolder, self).__init__(parent, readTimeLimitSec)
		self.name = name

	def _getPropertyFilePath(self):
		thisDirPath = os.path.dirname(inspect.getabsfile(MyPropertyHolder))
		return os.path.join(thisDirPath, 'properties', self.name)

	def isLocked(self):
		return FileLock.isLocked(self._getPropertyFilePath())

	def rawWrite(self, data):
		with open(self._getPropertyFilePath(), 'w') as f:
			f.write(data)

	def deleteFile(self):
		if os.path.exists(self._getPropertyFilePath()):
			os.remove(self._getPropertyFilePath())


#============================================================================
#============================================================================
class TestPropertyHolder(unittest.TestCase):

	def setUp(self):
		self.p = MyPropertyHolder('parent', None)
		self.c = MyPropertyHolder('child', self.p)
		self.p.clear()
		self.c.clear()
	 	self.p.clearAllCaches()

	def tearDown(self):
		self.p.clear()
		self.c.clear()
		self.assertEqual(self.p.isLocked(), False)
		self.assertEqual(self.c.isLocked(), False)
		self.__changeCacheValidtyUnCheckDuration(20)

	def testReadWhileNoFileExists(self):
		self.assertEqual(self.p.get('someKey'), None)
		self.assertEqual(self.p.get('someKey', 'default'), 'default')

	def testRemoveWhileNoFileExists(self):
		self.p.remove('someKey')

	def testNoKeyRemove(self):
		self.p.update('someKey', 1)
		self.assertEqual(self.p.get('someKey'), 1)
		self.assertEqual(self.p.get('differentKey'), None)
		self.assertEqual(self.p.getDict(), {'someKey':1})
		self.p.remove('someKey')
		self.assertEqual(self.p.get('someKey'), None)
		self.p.remove('someKey')
		self.assertEqual(self.p.get('someKey'), None)

	def testReadWrite(self):
		self.p.update('someKey', 1)
		self.assertEqual(self.p.get('someKey'), 1)
		self.assertEqual(self.p.getWithoutInheritance('someKey'), 1)

	def testReadInheritance(self):
		self.p.update('someKey', 1)
		self.assertEqual(self.c.get('someKey'), 1)

	def testReadNoInheritance(self):
		self.p.update('someKey', 1)
		self.assertEqual(self.c.getWithoutInheritance('someKey'), None)

	def testNonAsciiKeyReadFail(self):
		self.assertRaises(MyException, lambda: self.p.get(1))

	def testNonAsciiKeyWriteFail(self):
		self.assertRaises(MyException, lambda: self.p.update(1, 1))

	def testNonAsciiKeyRemoveFail(self):
		self.assertRaises(MyException, lambda: self.p.remove(1))

	def testClear(self):
		self.p.update('someKey', 1)
		self.p.clear()
		self.assertEqual(self.c.get('someKey'), None)

	def testCache(self):
		self.p.update('someKey', 1)
		self.p.deleteFile()
		self.assertEqual(self.c.get('someKey'), 1) #Cache exists.

	def __changeCacheValidtyUnCheckDuration(self, sec):
			import time, datetime
			from hohehohe2.utils.propertyHolder import _PropertyCache
			_PropertyCache._PropertyCache__CACHE_VALIDITY_UN_CHECK_DURATION = datetime.timedelta(seconds=sec)

	def testCacheTimeLimit(self):
		self.__changeCacheValidtyUnCheckDuration(0)
		self.p.update('someKey', 1)
		self.p.deleteFile()
		import time
		time.sleep(0.03)
		self.assertEqual(self.p.get('someKey'), None)

	def testCacheTimeLimit(self):
		self.__changeCacheValidtyUnCheckDuration(0)
		self.p.update('someKey', 1)

		#Rewrite cache.
		from hohehohe2.utils.propertyHolder import _PropertyCache
		oldCache, oldCacheTimeStamp, timeStampObtainedTime = self.p._PropertyHolder__cache._PropertyCache__cache[self.p._getPropertyFilePath()]
		newCache = {'someKey': 2}
		self.p._PropertyHolder__cache._PropertyCache__cache[self.p._getPropertyFilePath()] = (newCache, oldCacheTimeStamp, timeStampObtainedTime)

		import time
		time.sleep(0.03)
		self.assertEqual(self.p.get('someKey'), 2) #File time stamp will be checked, see unmodified, and cache used.

	def testClearAllCaches(self):
		self.c.update('someKey', 1)
		self.c.rawWrite('{"someKey": 2}')
		self.assertEqual(self.c.get('someKey'), 1) #Cache exists.
		self.p.clearAllCaches()
		self.assertEqual(self.c.get('someKey'), 2)

	def testCacheShared(self):
		self.p.update('someKey', 1)

		#Rewrite cache.
		from hohehohe2.utils.propertyHolder import _PropertyCache
		oldCache, oldCacheTimeStamp, timeStampObtainedTime = self.p._PropertyHolder__cache._PropertyCache__cache[self.p._getPropertyFilePath()]
		newCache = {'someKey': 2}
		self.p._PropertyHolder__cache._PropertyCache__cache[self.p._getPropertyFilePath()] = (newCache, oldCacheTimeStamp, timeStampObtainedTime)

		anotherP = MyPropertyHolder('parent', None)
		self.assertEqual(anotherP.get('someKey'), 2)

	def testFileReadFail(self):
		self.p = MyPropertyHolder('parent', None, readTimeLimitSec=0.02)
		self.p.update('someKey', 1)
		self.p.clearAllCaches()
		import time
		time.sleep(0.02) #Make sure the file time stamp changes.
		self.p.rawWrite('error data{')
		self.assertRaises(MyException, lambda: self.p.get('someKey'))

	def __writeFileInThread(self):
		import time
		time.sleep(0.03)
		self.p.rawWrite('{"someKey": 2}')

	def testFileReadRetry(self):
		import thread
		self.p = MyPropertyHolder('parent', None)
		self.p._PropertyHolder__READ_INTERVAL = 0.06 #Read retry interval.
		self.p.rawWrite('error data{')
		thread.start_new_thread(self.__writeFileInThread, ())
		self.assertEqual(self.p.get('someKey'), 2)

	def testFileReadRetry(self):
		self.assertFalse(self.p._getPropertyFilePath() in self.p._PropertyHolder__cache._PropertyCache__cache)
		self.p.get('someKey') #File check and create cache with empty data.
		self.assertTrue(self.p._getPropertyFilePath() in self.p._PropertyHolder__cache._PropertyCache__cache)
		self.assertEqual(self.p.getDict(), {})

	def testUpdate(self):
		self.p.update('someKey', 1)
		propDict = {'someKey': 2, 'someOtherKey': 3}
		self.p.updateDict(propDict)
		self.assertEqual(self.c.get('someKey'), 2)
		self.assertEqual(self.c.get('someOtherKey'), 3)

	def testUpdateCacheUpdate(self):
		self.p.update('someKey', 1)
		import time
		time.sleep(0.03)
		propDict = {'someKey': 2, 'someOtherKey': 3}
		oldCache, oldCacheTimeStamp, oldTimeStampObtainedTime = self.p._PropertyHolder__cache._PropertyCache__cache[self.p._getPropertyFilePath()]
		self.p.updateDict(propDict)
		newCache, newCacheTimeStamp, newTimeStampObtainedTime = self.p._PropertyHolder__cache._PropertyCache__cache[self.p._getPropertyFilePath()]
		self.assertNotEqual(oldCacheTimeStamp, newCacheTimeStamp)
		self.assertNotEqual(oldTimeStampObtainedTime, newTimeStampObtainedTime)

	def testRemove(self):
		self.p.update('someKey', 1)
		self.p.remove('someKey')
		self.assertEqual(self.c.get('someKey'), None)

	def testRemoveCacheUpdate(self):
		self.p.update('someKey', 1)
		import time
		time.sleep(0.03)
		oldCache, oldCacheTimeStamp, oldTimeStampObtainedTime = self.p._PropertyHolder__cache._PropertyCache__cache[self.p._getPropertyFilePath()]
		self.p.remove('someKey')
		newCache, newCacheTimeStamp, newTimeStampObtainedTime = self.p._PropertyHolder__cache._PropertyCache__cache[self.p._getPropertyFilePath()]
		self.assertNotEqual(oldCacheTimeStamp, newCacheTimeStamp)
		self.assertNotEqual(oldTimeStampObtainedTime, newTimeStampObtainedTime)


#============================================================================
#============================================================================
if __name__ == "__main__":
	unittest.main()
