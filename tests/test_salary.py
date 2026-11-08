from pathlib import Path
import pytest
from hh_parser.models import Salary
from hh_parser.config import EXCHANGE_RATE, UNKNOWN_CURRENCY

FIXTURES = Path(__file__).parent / 'fixtures'

@pytest.mark.parametrize(
	'raw, from_, to, currency',
	[
		# вилка
		('110 000 – 160 000 ₽ за месяц, на руки', 110000, 160000, '₽'),
		# неразрывные пробелы, как в реальном HTML hh.ru
		('110\u202f000 – 160\u202f000 ₽ за\xa0месяц', 110000, 160000, '₽'),
		# «от» — только нижняя граница
		('от 2 700 Br за месяц, на руки', 2700, None, 'Br'),
		# «до» — только верхняя граница
		('до 81 000 ₽ за месяц, до вычета налогов', None, 81000, '₽'),
		# одно число без «от/до» — фиксированная сумма
		('262 000 ₽ за месяц, на руки', 262000, 262000, '₽'),
		# валюта из нескольких символов
		("3 000 000 – 10 000 000 so'm за месяц", 3000000, 10000000, "so'm"),
		('500 000 – 550 000 ₸ за месяц, на руки', 500000, 550000, '₸'),
		('от 1 500 $', 1500, None, '$'),
	]
)

def test_from_text(raw, from_, to, currency):
	s = Salary.from_text(raw)

	assert s.from_ == from_
	assert s.to == to
	assert s.currency == currency

@pytest.mark.parametrize(
	'raw',
	[
		'не указано',
		'\nне указано\n',
		'',
		'   ',
	]
)

def test_from_text_without_salary_returns_none(raw):
	assert Salary.from_text(raw) is None

def test_all_salaries_do_not_crash():
	lines = (FIXTURES / 'salaries.txt').read_text(encoding='utf-8').splitlines()

	for line in lines:
		line = line.strip()
		if not line or line.startswith('---'):
			continue
		s = Salary.from_text(line)
		if s is not None:
			s.convert()

def test_convert_rub_keeps_values():
	s = Salary(100000, 150000, '₽').convert()

	assert (s.from_, s.to, s.currency) == (100000, 150000, '₽')

def test_convert_range():
	rate = EXCHANGE_RATE['₸']
	s = Salary(500000, 550000, '₸').convert()

	assert s.from_ == round(500000 * rate)
	assert s.to == round(550000 * rate)
	assert s.currency == '₽'

def test_convert_only_from():
	rate = EXCHANGE_RATE['Br']
	s = Salary(2700, None, 'Br').convert()

	assert (s.from_, s.to, s.currency) == (round(2700 * rate), None, '₽')

def test_convert_only_to():
	rate = EXCHANGE_RATE['$']
	s = Salary(None, 2000, '$').convert()

	assert (s.from_, s.to, s.currency) == (None, round(2000 * rate), '₽')

def test_convert_does_not_change_original():
	original = Salary(500000, 550000, '₸')
	original.convert()

	assert (original.from_, original.to, original.currency) == (500000, 550000, '₸')

def test_convert_unknown_currency_is_marked():
	s = Salary(1000, None, None).convert()
	assert (s.from_, s.to, s.currency) == (1000, None, UNKNOWN_CURRENCY)

