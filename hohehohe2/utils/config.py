# -*- coding: utf-8 -*-

import os, logging
from hohehohe2.utils import userMessage

#============================================================================
#============================================================================
class Config(object):
	"""
	設定ファイルを扱うクラス。
	設定ファイルは通常の設定ファイル見せかけたPythonファイルで、テキストエディタで開けるようにするため任意の拡張子を許容する。
	Config.__BASE_KEY_NAMEで指定されたキーにパスを入れるとその設定ファイルに記述された設定をオーバーライドする。
	設定ファイルのキーは文字列で、値はこのクラスでは任意のPythonオブジェクトを受け付ける。
	"""

	__BASE_KEY_NAME = 'base'

	def __init__(self, path=''):

		self.__config = {}
		"""
		設定データ。key(文字列)-値（任意のPythonオブジェクト）。
		"""

		if path:
			self.readOrUpdate(path)

	def readOrUpdate(self, path):
		"""
		pathで指定された設定ファイルを読み込む。
		設定ファイルにConfig.__BASE_KEY_NAMEで指定されたキーがあればその値をベースの設定ファイルとして読み込みマージする。
		既に設定ファイルが読み込まれていた場合は再読み込みを行う。
		"""
		path = os.path.normpath(os.path.normpath(path))
		config = {}
		try:
			while path:
				thisConfig = {}
				execfile(path, thisConfig)
				basePath = thisConfig.get(self.__BASE_KEY_NAME, None)
				thisConfig.update(config) #ベースを後に読むので今回読んだ設定ファイルを今までに読んだ設定ファイルでオーバーライドする。thisConfigはベースの設定ファイル。
				config = thisConfig
				if not basePath:
					break
				basePath = os.path.normpath(os.path.join(path, basePath)) #baseにディレクトリ相対指定を受け付けるようにする。
				if basePath == path:
					break #'.'や'\\'など不適切なパスが指定された場合の無限ループ回避。
				path = basePath
		except :
			msg = 'Reading config file %s failed' % repr(path)
			logging.error(msg)
			userMessage.showError(msg)
			import traceback
			logging.error(traceback.format_exc())
			raise

		#execfileが作ったごみ（__builtins__など）を削除。
		for key in config.keys():
			if key.startswith('__'):
				del config[key]

		self.__config = config

	def get(self, key):
		"""
		configのキーを指定して値を取り出す。そのキーに対する値がなければNoneを返す。
		"""
		return self.__config.get(key, None)



#============================================================================
#============================================================================
_config = Config()
"""
デフォルトのconfigオブジェクト。通常はこのオブジェクトを使うだけで十分。readOrUpdate()とget()でアクセスする。
"""


#============================================================================
#============================================================================
def readOrUpdate(path):
	"""
	デフォルトconfigオブジェクトに設定ファイルを読み込ませる。
	"""
	_config.readOrUpdate(path)


#============================================================================
#============================================================================
def get(key):
	"""
	デフォルトconfigオブジェクトのキーを指定して値を取り出す。そのキーに対する値がなければNoneを返す。
	"""
	return _config.get(key)
