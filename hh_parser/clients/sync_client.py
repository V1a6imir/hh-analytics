from hh_parser.config import HEADERS, URL, CARD_URL
import requests


class HHClient:
	
	def __init__(self, headers=HEADERS, url=URL, card_url=CARD_URL):
		self.headers = headers
		self.url = url
		self.card_url = card_url

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

		r = requests.get(self.url, params=payload, headers=self.headers)
		
		html = r.text
		return html

	def get_vacancy_page(self, vacancy_id: str):

		full_card_url = self.card_url + vacancy_id
		r = requests.get(full_card_url, headers=self.headers)

		card_html = r.text
		return card_html

	

