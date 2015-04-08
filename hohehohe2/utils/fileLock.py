# -*- coding: utf-8 -*-

import os, time, datetime, logging
from hohehohe2.utils.myException import MyException


#============================================================================
#============================================================================
class _FileLockBase(object):

	__PREFIX = '.lock_'
	"""
	ファイルロック（ダミーの空ディレクトリ）の名前につけるプレフィックス。
	"""

	_SLEEP_SEC = 0.5
	"""
	ファイルロックが取得できない場合に次にトライするまでの秒数。
	"""

	def __init__(self, filePath, timeLimitSec=5.0):
		self._filePath = filePath = os.path.abspath(os.path.normpath(filePath))
		self._timeLimit = datetime.timedelta(seconds=timeLimitSec)
		self._lockFilePath = self.getLockFilePath(filePath)

	@classmethod
	def isLocked(cls, filePath):
		return os.path.exists(cls.getLockFilePath(filePath))

	@classmethod
	def getLockFilePath(cls, filePath):
		return os.path.join(os.path.dirname(filePath), cls.__PREFIX + os.path.basename(filePath))


#============================================================================
#============================================================================
class FileLock(_FileLockBase):
	"""
	ファイルロック機構。複数のプロセス（ユーザー）が同時にファイル書き込みを行わないようロックするためのもの。

	使い方。この例ではファイルリードとライトをアトミックに行う。リードとライトの間で他のユーザーが行ったファイルの更新がなくならないようロックを行う。
		with FileLock(filePath):
			with open(filePath, 'r') as f:
				fileContents = f.read()
				fileContents = fileContents[::-1] #例としてファイル内の文字を逆順にならべる。
			with open(filePath, 'w') as f:
				fileContents = f.write(fileContents)
	"""

	def __enter__(self):
		startTime = datetime.datetime.now()
		while(True):
			try:
				os.mkdir(self._lockFilePath)
				return
			except:
				if datetime.datetime.now() - startTime > self._timeLimit:
					msg = 'Could not lock file ' + repr(self._filePath)
					logging.error(msg)
					import traceback
					logging.error(traceback.format_exc())
					raise MyException(msg)
			time.sleep(self._SLEEP_SEC)

	def __exit__(self, exc_type, exc_value, traceback):
		try:
			os.rmdir(self._lockFilePath)
		except:
			msg = 'Could not delete a lock file ' + repr(self._lockFilePath)
			logging.warning(msg)
		return True


#============================================================================
#============================================================================
class FileLockWait(_FileLockBase):
	"""
	ファイルロック機構。自分ではロックファイルを作らないがロックが解放されるまで待つ。使い方はFileLockと同じ。
	注：ロックファイルを作成しないのでFileLockよりも高速だがwithに入ってからも他のプロセスがファイルを編集する可能性がある。
	注：厳密な排他処理が必要な場合はFileLockを用いること。
	"""

	def __enter__(self):

		startTime = datetime.datetime.now()
		while(datetime.datetime.now() - startTime < self._timeLimit):
			if not os.path.exists(self._lockFilePath):
				break
			time.sleep(self._SLEEP_SEC)

	def __exit__(self, exc_type, exc_value, traceback):
		return True
