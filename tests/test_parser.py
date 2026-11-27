from pathlib import Path
import pytest
from hh_parser.parsers import parse_search_page_html, text_or_none, parse_vacancy_page_html
from bs4 import BeautifulSoup
from hh_parser.models import Salary



FIXTURES = Path(__file__).parent / 'fixtures'

@pytest.mark.parametrize(
		'result',
		[
			20
		]
)

def test_len_of_search_page(result):

	html = (FIXTURES / 'search_page.html').read_text(encoding='utf-8')
	
	_len = len(parse_search_page_html(html))

	assert _len == result

@pytest.mark.parametrize(
		'index, vacancy_id, vacancy_name, rating, company_name, location, experience',
		[
			(
				0,
				'139876655',
				'Наладчик-программист \\ оператор станков с ЧПУ (токарная группа)',
				'3.3',
				'Хохлов Максим',
				'Санкт-Петербург',
				'between1And3'
			),
			(
				1,
				'139812490',
				'Программист-преподаватель',
				None,
				'Kiber One',
				'Коломна, улица Октябрьской Революции, 362',
				'noExperience'
			)
		]
)

def test_card_els(index, vacancy_id, vacancy_name, rating,  company_name, location, experience):
	html = (FIXTURES / 'search_page.html').read_text(encoding='utf-8')
		
	cards = parse_search_page_html(html)

	assert cards[index]['id'] == vacancy_id
	assert cards[index]['vacancy_name'] == vacancy_name
	assert cards[index]['rating'] == rating
	assert cards[index]['company_name'] == company_name
	assert cards[index]['location'] == location
	assert cards[index]['experience'] == experience

def test_experience():
	html = (FIXTURES / 'search_page.html').read_text(encoding='utf-8')
		
	cards = parse_search_page_html(html)
	assert all(card['experience'] is not None for card in cards)
	


def test_if_none():

	value = BeautifulSoup('<div></div>', 'html.parser')
	check = text_or_none(value, '[data-qa="serp-item__title-text"]')
	assert check is None

def test_if_have_text():

	value = BeautifulSoup('<div>        bababa c bebebe   </div>', 'html.parser')
	check = text_or_none(value, 'div')
	assert check == 'bababa c bebebe'



def test_vacancy_with_skills():

	html = (FIXTURES / 'vacancy_with_skills.html').read_text(encoding='utf-8')

	vacancy = parse_vacancy_page_html(html)

	assert vacancy['skills'] == ['.Net', 'Elasticsearch', 'vLLM', 'MCP', 'RAG']



def test_vacancy_without_skills():

	html = (FIXTURES / 'vacancy_without_skills.html').read_text(encoding='utf-8')

	vacancy = parse_vacancy_page_html(html)

	assert vacancy['skills'] == []



def test_salary():

	html = (FIXTURES / 'vacancy_with_skills.html').read_text(encoding='utf-8')

	vacancy = parse_vacancy_page_html(html)

	result = Salary.from_text(vacancy['salary'])

	assert result.to == 300000




