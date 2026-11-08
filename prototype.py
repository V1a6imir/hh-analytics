import requests
from bs4 import BeautifulSoup
import time
import json


def text_or_none(card, selector):
	el = card.select_one(selector)
	return el.get_text(' ', strip=True) if el else None



url = 'https://hh.ru/search/vacancy'
query = 'machine learning'
all_titles = []
page = 0
vacancies = []

while page < 2:

	params = {
		'text': query,
		'page': page
	}
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36'
	}
	r = requests.get(url, params=params, headers=headers)

	soup = BeautifulSoup(r.text, 'html.parser')

	cards = soup.select('[data-qa="vacancy-serp__vacancy"]')
	if not cards:
		break

	for card in cards:

		vacancy = {}

		experience = card.select_one('[data-qa*="vacancy-serp__vacancy-work-experience"]')

		vacancy = {
			'salary': text_or_none(card, '[class="magritte-text___pbpft_5-3-17_xhh magritte-text_style-primary___AQ7MW_5-3-17_xhh magritte-text_typography-label-1-regular___pi3R-_5-3-17_xhh"]'),
			
			'vacancy_name': text_or_none(card, '[data-qa="serp-item__title-text"]'),
			'company_name': text_or_none(card, '[data-qa="vacancy-serp__vacancy-employer-text"]'),
			'location': text_or_none(card, '[data-qa="vacancy-serp__vacancy-address"]'),
			'experience': experience['data-qa'].removeprefix('vacancy-serp__vacancy-work-experience-') if experience else None,
			'rating': text_or_none(card, '[data-qa="company-review-rating-value"]')
			
		}


		# Получаем навыки для вакансии

		id = card.select_one('div[id]')['id']
		card_url = f'https://hh.ru/vacancy/{id}'

		card_r = requests.get(card_url, headers=headers)
		card_soup = BeautifulSoup(card_r.text, 'html.parser')

		skills = card_soup.find_all('li', attrs={'data-qa': 'skills-element'})
		skill_names = [s.get_text(strip=True).replace('\xa0', '').replace('\u202f', '') for s in skills]

		vacancy['skills'] = skill_names
		vacancy['id'] = id

		vacancies.append(vacancy)
	
	page+=1
	time.sleep(1)


with open('cards.json', 'w', encoding='utf-8') as f:
	json.dump(vacancies, f, ensure_ascii=False, indent=2)



# 	all_titles += [t.get_text(strip=True) for t in titles]
# 	print(f'page: {page + 1}: {len(titles)} vacancies')

# 	page += 1
# 	time.sleep(1)

# print(f'всего: {len(all_titles)}')

# print(all_titles)