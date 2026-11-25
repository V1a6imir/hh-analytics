# ClientError
# 	NotFoundError
#	BlockedError
#	RetryableError
# 		NetworkError
# 		TooManyRequestsError
# 		ServerError

class ClientError(Exception):
	"""Не смогли выполнить запрос"""

class NotFoundError(ClientError):
	"""Страница не найдена"""

class BlockedError(ClientError):
	"""Сайт заблокировал запросы"""

class RetryableError(ClientError):
	"""Запрос можно повторить"""

class NetworkError(RetryableError):
	"""Нет сети, нужен timeout"""

class TooManyRequestsError(RetryableError):
	"""Слишком много запросов нужна пауза"""

class ServerError(RetryableError):
	"""Ошибка сервера/сайта"""
