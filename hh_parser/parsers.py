from bs4 import BeautifulSoup


def parse_search_page_html(search_page):

	soup = BeautifulSoup(search_page, 'html.parser')
	cards = soup.select('[data-qa~="vacancy-serp__vacancy"]')
	return cards
	