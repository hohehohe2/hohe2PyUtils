# -*- coding: utf-8 -*-

import os, unittest, inspect, time, threading
from hohehohe2.utils.fileLock import FileLock
from hohehohe2.utils.myException import MyException


#============================================================================
#============================================================================
class TestFileLock(unittest.TestCase):

	def setUp(self):
		self.__deleteFile()

	def tearDown(self):
		self.__deleteFile()

	def __getFilePath(self):
		return os.path.join(os.path.dirname(inspect.getabsfile(TestFileLock)), 'fileLockTestFile.txt')

	def __writeFile(self, text):
		with open(self.__getFilePath(), 'w') as f:
			f.write(text)

	def __readFile(self):
		with open(self.__getFilePath(), 'r') as f:
			return f.read()

	def __deleteFile(self):
		try:
			os.remove(self.__getFilePath())
		except:
			pass

	def __writeLockInThread(self, sleepFirst, sleepAfterWrite):
		time.sleep(sleepFirst)
		with FileLock(self.__getFilePath()):
			self.__writeFile('tako')
			time.sleep(sleepAfterWrite)

	def testLock(self):
		with FileLock(self.__getFilePath()):
			pass

	def testLockWaitInThread(self):
		import thread
		th = threading.Thread(target = self.__writeLockInThread, args = (0, 0.1))
		time.sleep(0.05)
		with FileLock(self.__getFilePath()):
			self.assertEqual(self.__readFile(), 'tako')

	def testLockWaitTimeLimitFail(self):
		try:
			FileLock._SLEEP_SEC = 0
			th = threading.Thread(target = self.__writeLockInThread, args = (0, 0.1))
			th.start()
			time.sleep(0.05)
			def failMethod():
				with FileLock(self.__getFilePath(), 0): #No wait.
					pass
			self.assertRaises(MyException, failMethod)
			th.join()
		except:
			del FileLock._SLEEP_SEC


#============================================================================
#============================================================================
if __name__ == "__main__":
	unittest.main()
