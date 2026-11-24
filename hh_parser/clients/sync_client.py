from hh_parser.config import HEADERS, URL, CARD_URL
import requests


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

		return self._get_html(URL, params=payload)

	
	def get_vacancy_page(self, vacancy_id):

		full_card_url = CARD_URL + str(vacancy_id)
		return self._get_html(full_card_url)

	def _get_html(self, url, params=None):

		r = self.session.get(url, params=params, headers=HEADERS)
		return r.text

	

