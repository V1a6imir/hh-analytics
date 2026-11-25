from hh_parser.config import HEADERS, URL, CARD_URL, TIMEOUT, LEN_OF_HTML, MAX_RETRIES, REQUEST_DELAY, PAUSE
from hh_parser.clients.exceptions import ClientError, NotFoundError, BlockedError, RetryableError, NetworkError, ServerError, TooManyRequestsError
import requests
import time


class HHClient:
	
	def __init__(self):
		self.session = requests.Session()

	def get_search_page(
			self, query,
			page_number=1, region=None,
			salary_mode=None, district=None,
			metro=None, work_schedule_by_days=None
	):
		
		
		if page_number <= 0:
			raise ValueError(f'Нумерация страниц начинается с 1, у Вас {page_number}')
		
		payload = {
			'text': query,
			'page': page_number - 1,
			'area': region,
			'salary_mode': salary_mode,
			'district': district,
			'metro': metro,
			'work_schedule_by_days': work_schedule_by_days
		}

		return self._make_attempts(URL, params=payload)				

	
	def get_vacancy_page(self, vacancy_id):

		full_card_url = CARD_URL + str(vacancy_id)

		return self._make_attempts(full_card_url)

	def _get_html(self, url, params=None):

		try:
			r = self.session.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
		
		except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
			raise NetworkError(f'Ошибка соединения - нужен timeout | {url}') from e
		
		except requests.exceptions.RequestException as e:
			raise ClientError(f'Ошибка соединения | {url}') from e
		
		
		if r.status_code == 404 and len(r.text) < LEN_OF_HTML:
			raise BlockedError(f'Не удалось получить страницу | {r.url} | {r.status_code}')
		
		if r.status_code == 404 and len(r.text) >= LEN_OF_HTML:
			raise NotFoundError(f'Не удалось найти страницу | {r.url} | {r.status_code}')

		if r.status_code == 403:
			raise BlockedError(f'Доступ заблокирован | {r.url} | {r.status_code}')

		if r.status_code >= 500:
			raise ServerError(f'Проблемы на сервере | {r.url} | {r.status_code}')

		if r.status_code == 429:
			raise TooManyRequestsError(f'Слишком частые запросы - нужна пауза | {r.url} | {r.status_code}')

		if r.status_code != 200:
			raise ClientError(f'Ошибка | {r.url} | {r.status_code}')
		return r.text

	def _make_attempts(self, url, params=None):

		time.sleep(PAUSE)
		
		for attempt in range(0, MAX_RETRIES):

			try:
				return self._get_html(url, params)
			
			except RetryableError:
				print(f'Попытка {attempt + 1}: не удалось получить страницу')

				if attempt == MAX_RETRIES - 1:
					raise
				
				time.sleep(REQUEST_DELAY ** attempt)

	

