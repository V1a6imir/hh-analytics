from bs4 import BeautifulSoup


def text_or_none(card, selector):
	el = card.select_one(selector)
	return el.get_text(strip=True) if el else None

def parse_search_page_html(search_page):

	soup = BeautifulSoup(search_page, 'html.parser')
	cards = soup.select('[data-qa~="vacancy-serp__vacancy"]')
	vacancies = []

	for card in cards:

		experience = card.select_one('[data-qa^="vacancy-serp__vacancy-work-experience"]')

		vacancy = {
			'id': card.select_one('div[id]')['id'],
			'vacancy_name': text_or_none(card, '[data-qa="serp-item__title-text"]'),
			'rating': text_or_none(card, '[data-qa="company-review-rating-value"]'),
			'company_name': text_or_none(card, '[data-qa="vacancy-serp__vacancy-employer-text"]'),
			'location': text_or_none(card, '[data-qa="vacancy-serp__vacancy-address"]'),
			'experience': experience['data-qa'].removeprefix('vacancy-serp__vacancy-work-experience-') if experience else None

		}

		vacancies.append(vacancy)
		
	return vacancies

def parse_vacancy_page_html(vacancy_page):


	soup = BeautifulSoup(vacancy_page, 'html.parser')
	
	salary = text_or_none(soup, '[data-qa="vacancy-salary"]')
	# find_all вернет пустой список если ничего не найдет
	skills = soup.find_all('li', attrs={'data-qa': 'skills-element'})
	skill_names = [s.get_text(strip=True).replace('\xa0', ' ').replace('\u202f', ' ') for s in skills]

	return {'salary': salary, 'skills': skill_names}


