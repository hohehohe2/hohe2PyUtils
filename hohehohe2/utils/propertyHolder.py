# -*- coding: utf-8 -*-

"""
propertyモジュール。
propertyは各種オブジェクトに付属するkey-valueペアで、keyはASCII文字列。
オブジェクトはparentを持ち継承をサポートする。
"""

import os, logging, time, datetime, json
from hohehohe2.utils.fileLock import FileLock
from hohehohe2.utils.myException import MyException


#============================================================================
#============================================================================
class _PropertyCache(object):
	"""
	propertyのキャッシュ。
	"""

	__CACHE_VALIDITY_UN_CHECK_DURATION = datetime.timedelta(seconds=20)
	"""
	効率化のためキャッシュをとってから一定時間内であればキャッシュ取得後他のプロセス（ユーザー）によりPropertyが更新されているかどうかのチェックを省く。
	例えば複数AssetのPropertyをループして取得するとき継承元である同一Project等のPropertyファイルタイムスタンプを複数回チェックするのを抑止する。
	この時間内では他プロセス（他ユーザー）によるPropertyの変更が反映されなくなる。自分自身による更新は常に反映される。
	"""

	def __init__(self):
		self.__cache = {}
		"""
		{filePath: (cache, cacheTimeStamp, timeStampObtainedTime)}
		keyはファイルパス。
		valueはキャッシュデータ、キャッシュファイルのタイムスタンプ、最後にタイムスタンプを取得したときの時刻。
		キャッシュファイルのタイムスタンプはファイル更新チェックのため用いられる。
		ファイル更新チェックもディスクアクセスが発生するため最後にチェックしたときから一定時間内ならファイル更新されていないものとしてチェックを省く。
		最後にタイムスタンプを取得したときの時刻はそのために用いられる。
		"""

	def get(self, filePath):
		"""
		filePathで指定されたpropertyのキャッシュを得る。
		キャッシュがない場合はNoneを返す。
		"""
		cache, cacheTimeStamp, timeStampObtainedTime = self.__cache.get(filePath, (None, None, None))
		if timeStampObtainedTime is None:
			#キャッシュがない。
			return None

		#効率化のため、最後にタイムスタンプをチェックしたときから一定時間内であれば他のプロセス（ユーザー）によりPropertyが更新されているかどうかのチェックを省く。
		if datetime.datetime.now() - timeStampObtainedTime < self.__CACHE_VALIDITY_UN_CHECK_DURATION:
			return cache

		#Propertyファイルが存在しないのでキャッシュとタイムスタンプを更新して終了。
		if not os.path.exists(filePath):
			#別プロセス（他ユーザー）によりファイル自体削除されていた。キャッシュとタイムスタンプ等を更新して終了。
			self.set(filePath, {})
			return {}

		#別プロセス（他ユーザー）によるpropertyファイルの更新チェック。キャッシュを保存した時からタイムスタンプが更新されていなければそのキャッシュを用いる。
		try:
			if os.stat(filePath).st_mtime == cacheTimeStamp:
				return cache
			else:
				#ファイルが更新されていた。キャッシュを取り除いておく。
				del self.__cache[filePath]
				return None

		except:

			if not os.path.exists(filePath):
				#上の処理の途中で別プロセス（他ユーザー）がファイルを削除するとここにくる場合がある。キャッシュとタイムスタンプ等を更新して終了。
				self.set(filePath, {})
				return {}

			logging.error('Unknown cache read error ' + repr(filePath))
			import traceback
			exc = traceback.format_exc() #ロギング用にtraceback表示の記録。
			logging.error(exc)
			raise

	def set(self, filePath, cache):
		"""
		filePathで指定されたpropertyのキャッシュを保存する。cacheが空dictでなければファイルは存在していなければならない。
		"""

		#NOTE: datetime.now()で取得した時刻とファイルのタイムスタンプを比較しないこと。
		#NOTE: そのようなコードはファイルサーバーの時刻とローカルマシンの時刻が同期されていなければ正常動作しない。
		#NOTE:　またサーバーとの通信やファイル書き込み時間などのため挙動が安定しない。

		now = datetime.datetime.now()

		if cache:
			cacheTimeStamp = os.stat(filePath).st_mtime
		else:
			#Propertyファイルがなくても空dictをキャッシュに入れておき「Propertyがないこと」を覚えておく。
			cacheTimeStamp = 0 #ダミー。値は使われない。

		self.__cache[filePath] = (cache, cacheTimeStamp, now)

	def remove(self, filePath):
		"""
		filePathで指定されたpropertyのキャッシュを削除する。
		"""
		if filePath in self.__cache:
			del self.__cache[filePath]

	def clear(self):
		"""
		キャッシュを削除する。
		"""
		self.__cache = {}


#============================================================================
#============================================================================
class PropertyHolder(object):
	"""
	propertyを保持できるオブジェクト。
	"""

	__READ_INTERVAL = 0.5
	"""
	ファイルリードが失敗した時に次にトライするまでの間隔。
	"""

	__cache = _PropertyCache()
	"""
	継承を含めないpropertyのキャッシュ。クラスメンバとして全オブジェクトで共有されるようにしておく。
	"""

	@classmethod
	def clearAllCaches(cls):
		"""
		全てのキャッシュを削除する。
		"""
		cls.__cache.clear()

	def __init__(self, parent, readTimeLimitSec=3.0):
		self.__parent = parent

		self.__readTimeLimit = datetime.timedelta(seconds=readTimeLimitSec)
		"""
		Propertyファイルの読み込みに失敗したとき再トライを続ける時間。
		"""

	def get(self, key, default=None):
		"""
		継承を含めたpropertyのkeyをとってvalueを返す。 keyに対するvalueがなければdefaultを返す。
		何度も呼ぶ場合は都度ファイルアクセスが発生しないようgetDict()を用いること。
		"""
		filePath = os.path.abspath(os.path.normpath(self._getPropertyFilePath()))
		if not isinstance(key, basestring):
			msg = 'Bug found. Tried to get a property with non-string key "%s" from file %s' % (repr(key), repr(filePath))
			logging.error(msg)
			raise MyException(msg)

		return self.getDict().get(key, default)

	def getDict(self):
		"""
		継承を含めたpropertyのdictを返す。
		"""

		propDict = self.getDictWithoutInheritance()

		if not self.__parent:
			return propDict

		#継承。
		mergedPropDict = self.__parent.getDict()
		mergedPropDict.update(propDict)
		return mergedPropDict

	def getWithoutInheritance(self, key, default=None):
		"""
		継承を含めないpropertyのkeyをとってvalueを返す。 keyに対するvalueがなければdefaultを返す。
		何度も呼ぶ場合は都度ファイルアクセスが発生しないようgetDictWithoutInheritance()を用いること。
		"""
		filePath = os.path.abspath(os.path.normpath(self._getPropertyFilePath()))
		if not isinstance(key, basestring):
			msg = 'Bug found. Tried to get a property with non-string key "%s" from file %s' % (repr(key), repr(filePath))
			logging.error(msg)
			raise MyException(msg)
		return self.getDictWithoutInheritance().get(key, default)

	def getDictWithoutInheritance(self):
		"""
		継承を含めないpropertyのdictを返す。
		"""
		filePath = os.path.abspath(os.path.normpath(self._getPropertyFilePath()))

		cache = self.__cache.get(filePath)
		if not cache is None:
			#キャッシュがみつかった。
			return cache

		#Propertyファイル読み込み。
		propertyDict = self.__getDictWithoutInheritance(filePath)

		#キャッシュ更新。
		self.__cache.set(filePath, propertyDict)

		return propertyDict

	def __getDictWithoutInheritance(self, filePath):
		"""
		Propertyファイルリード。キャッシュは使わない。
		"""

		if not os.path.exists(filePath):
			return {}

		#読み込みに失敗すればself.__readTimeLimitの時間だけ再トライを続ける。
		startTime = datetime.datetime.now()
		while(datetime.datetime.now() - startTime < self.__readTimeLimit):
			#JSONフォーマットでdictを読み込むので正常なファイルでは{と}のペアが対応しており、他プロセス（他ユーザー）の書き込み途中に読み込んだ場合特殊な場合を除いて例外を送出する。
			#他プロセス（他ユーザー）によるライト途中の読み込みはJSON読み込みの失敗で検知できるものとし、ファイルロックやロックファイル有無の確認は行わない。
			try:
				with open(filePath, 'r') as f:
					propertyDict = json.load(f)
				break #読み込み成功。
			except:
				if not os.path.exists(filePath):
					#読み込もうとしている最中に他プロセス（ユーザー）によってファイルが削除された。
					return {}
				import traceback
				exc = traceback.format_exc() #ロギング用にtraceback表示の記録。
				time.sleep(self.__READ_INTERVAL)

		else:
			#読み込み失敗。
			msg = 'Failed reading property file ' + repr(filePath)
			logging.error(msg)
			logging.error(exc)
			raise MyException(msg)

		return propertyDict

	def update(self, key, value):
		"""
		このオブジェクトのpropertyをkey-valueで更新する。
		キーはASCII文字列でなければならない。
		何度も呼ぶ場合は都度ファイルアクセスが発生しないようupdateDict()を用いること。
		更新されたpropertyのdictを返す。
		"""
		return self.updateDict({key:value})

	def updateDict(self, propDict):
		"""
		このオブジェクトのpropertyをdictで更新する。
		dictのキーはASCII文字列でなければならない。
		更新されたpropertyのdictを返す。
		"""

		filePath = os.path.abspath(os.path.normpath(self._getPropertyFilePath()))

		#全てのkeyがASCII文字列であるかチェック。
		for key in propDict.keys():
			if not isinstance(key, basestring):
				msg = 'Bug found. Tried to update a property file %s with non-string key "%s".' % (filePath, repr(key))
				logging.error(msg)
				raise MyException(msg)

		#propertyファイル更新。
		with FileLock(filePath): #propertyファイルのリードとライトをアトミックに行う。
			currentDict = self.__updateDict(propDict)

		#キャッシュ更新。
		self.__cache.set(filePath, currentDict)

		return currentDict

	def __updateDict(self, propDict):

		filePath = os.path.abspath(os.path.normpath(self._getPropertyFilePath()))

		#現在のpropertyをファイルからロード。
		currentDict = self.__getDictWithoutInheritance(filePath)

		#propDictをマージ。
		currentDict.update(propDict)

		if not currentDict:
			#空dictならPropertyファイルを削除。
			self.__clear(filePath)
			return {}

		#Propertyファイルライト。
		try:
			with open(filePath, 'w') as f:
				json.dump(currentDict, f)
		except IOError:
			msg = 'Property file write IO error ' + repr(filePath) + '.'
			logging.error(msg)
			import traceback
			logging.error(traceback.format_exc())
			raise
		except:
			msg = 'Unexpected property write error.' % repr(filePath)
			logging.error(msg)
			import traceback
			logging.error(traceback.format_exc())
			raise

		return currentDict

	def remove(self, key):
		"""
		このオブジェクトのkeyで指定されたpropertyを削除する。存在しなければ何もしない。
		キーはASCII文字列でなければならない。
		更新されたpropertyのdictを返す。
		"""
		filePath = os.path.abspath(os.path.normpath(self._getPropertyFilePath()))

		if not isinstance(key, basestring):
			msg = 'Bug found. Tried to remove a property from file %s with non-string key "%s".' % (filePath, repr(key))
			logging.error(msg)
			raise MyException(msg)

		#propertyファイル更新。
		with FileLock(filePath): #propertyファイルのリードとライトをアトミックに行う。
			currentDict = self.__remove(key, filePath)

		#キャッシュ更新。
		self.__cache.set(filePath, currentDict)

		return currentDict

	def __remove(self, key, filePath):

		#現在のpropertyをファイルからロード。
		currentDict = self.__getDictWithoutInheritance(filePath)

		#keyを削除。
		if key in currentDict:
			del currentDict[key]

		if not currentDict:
			#空dictならPropertyファイルを削除。
			self.__clear(filePath)
			return {}

		#Propertyファイルライト。
		try:
			with open(filePath, 'w') as f:
				json.dump(currentDict, f)
		except IOError:
			msg = 'Property file write IO error ' + repr(filePath) + '.'
			logging.error(msg)
			import traceback
			logging.error(traceback.format_exc())
			raise
		except:
			msg = 'Unexpected property write error.' % repr(filePath)
			logging.error(msg)
			import traceback
			logging.error(traceback.format_exc())
			raise

		return currentDict

	def clear(self):
		"""
		このオブジェクトのpropertyを削除する。
		親オブジェクトのpropertyは削除しないので継承された値は削除されない。
		"""
		filePath = os.path.abspath(os.path.normpath(self._getPropertyFilePath()))

		with FileLock(filePath):
			self.__clear(filePath)

		self.__cache.set(filePath, {})

	def __clear(self, filePath):
		if os.path.exists(filePath):
			os.remove(filePath)

	def _getPropertyFilePath(self):
		"""
		propertyファイルへのパスを返す。propertyファイルは存在していなくても構わない。
		"""
		#Must be overridden at a subclass.
		raise NotImplementedError
