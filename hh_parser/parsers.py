from bs4 import BeautifulSoup
from pathlib import Path


def parse_search_page_html(search_page):

	soup = BeautifulSoup(search_page, 'html.parser')
	cards = soup.select('[data-qa~="vacancy-serp__vacancy"]')
	vacancies = []

	for card in cards:
		vacancy = {
			'id': card.select_one('div[id]')['id'],
			'vacancy_name': card.select_one('[data-qa="serp-item__title-text"]').get_text(strip=True)
		}
		vacancies.append(vacancy)
		
	return vacancies
