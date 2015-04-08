# -*- coding: utf-8 -*-

import os, logging, imp
from hohehohe2.utils.myException import MyException
from hohehohe2.utils import userMessage

#============================================================================
#============================================================================
class PluginReader(object):
	"""
	汎用プラグイン読み込み機構。
	プラグインはget(プラグイン名)で取得できる。
	プラグインはモジュールオブジェクトで、プラグイン名がfooの場合__init__で引数に指定されたpluginDirPathにあるfoo.pyがそのモジュールとして読み込まれる。
	"""
	def __init__(self, pluginDirPath, defaultPluginName=None):
		"""
		pluginDirPath プラグイン格納ディレクトリパス
		defaultPluginName 指定されたプラグインがなかったときに使われるプラグイン名
		"""

		self.__pluginDirPath = pluginDirPath
		"""
		プラグインディレクトリパス。
		"""

		self.__loadedPluginCache = {} #{pluginName:plugin module object}.
		"""
		今までに読み込んだプラグインのキャッシ。
		"""

		self.__defaultPluginName = defaultPluginName
		"""
		デフォルトプラグイン名。
		"""

	def get(self, pluginName):
		"""
		プラグインを取得する。既に読み込まれていれば再ロードせずキャッシュされたものを返す。
		"""

		#ロードするプラグインファイルの特定。
		pluginFilePath = self._getPluginFilePath(pluginName)
		if not pluginFilePath:
			#プラグインファイルがない。デフォルトプラグインが指定されていればそれを使う。
			if (self.__defaultPluginName):
				pluginName = self.__defaultPluginName
				pluginFilePath = self._getPluginFilePath(pluginName)

		if not pluginFilePath:
				msg = 'Plugin ' + repr(pluginName) + ' not found.'
				logging.error(msg)
				import traceback
				logging.error(traceback.format_exc())
				userMessage.showError(msg)
				raise MyException(msg)

		#キャッシュを探す。
		plugin = self.__loadedPluginCache.get(pluginName)
		if plugin:
			return plugin

		#ロード。
		try:
			if pluginFilePath.endswith('py'):
				plugin = imp.load_source(pluginName, pluginFilePath)
			else:
				plugin = imp.load_compiled(pluginName, pluginFilePath)
		except:
			msg = 'Failed reading plugin file ' + repr(pluginFilePath) + ' .'
			logging.error(msg)
			import traceback
			logging.error(traceback.format_exc())
			userMessage.showError(msg)
			raise

		self.__loadedPluginCache[plugin] = plugin
		return plugin

	def clearCache(self):
		"""
		読み込んだプラグインのキャッシュをクリアする。
		このメソッドを呼んだ後でも古いプラグインがプログラム上のどこかに残っていて使われ続ける可能性があるので注意。
		"""
		self.__loadedPluginCache.clear()

	def _getPluginFilePath(self, pluginName):
		for ext in ['.py', '.pyc', '.pyo']:
			pluginFileName = pluginName + ext
			pluginFilePath = os.path.join(self.__pluginDirPath, pluginFileName)
			if os.path.exists(pluginFilePath):
				return pluginFilePath
