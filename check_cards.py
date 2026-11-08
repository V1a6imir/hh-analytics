import json
from hh_parser.models import Vacancy



with open('/Users/vladimirmonastirsky/selfedu/парсер_ХХ/cards.json', 'r', encoding='utf-8') as f:
	cards = json.load(f)


for card in cards:
	v = Vacancy.from_dict(card)
	print(v)


