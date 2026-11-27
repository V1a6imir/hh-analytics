from pathlib import Path
import pytest
from hh_parser.parsers import parse_search_page_html

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
		'vacancy_id, vacancy_name',
		[
			(
				'139876655',
				'Наладчик-программист \\ оператор станков с ЧПУ (токарная группа)'
			)
		]
)

def test_card_els(vacancy_id, vacancy_name):
	html = (FIXTURES / 'search_page.html').read_text(encoding='utf-8')
		
	cards = parse_search_page_html(html)

	assert cards[0]['id'] == vacancy_id
	assert cards[0]['vacancy_name'] == vacancy_name
	


