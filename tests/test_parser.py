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

