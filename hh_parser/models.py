import re
from hh_parser.config import EXCHANGE_RATE, UNKNOWN_CURRENCY

class Salary:

	def __init__(self, from_, to, currency):
		
		self.from_ = from_
		self.to = to
		self.currency = currency

	
	@classmethod
	def from_text(cls, raw):
		
		text = raw.replace(' ', '').replace('\xa0', '').replace('\u202f', '')

		price =  [int(x) for x in re.findall(r'\d+', text)]

		currency = None
		for symbol in EXCHANGE_RATE:
			if symbol in text:
				currency = symbol
				break

						
		if len(price) == 1:
			text = text.strip().lower()
			if text.startswith('до'):
				return cls(from_=None, to=price[0], currency=currency)

			elif text.startswith('от'):
				return cls(from_=price[0], to=None, currency=currency)
			
			else:
				return cls(from_=price[0], to=price[0], currency=currency)

		elif len(price) == 0:
			return None
		else:
			return cls(from_=price[0], to=price[1], currency=currency)

		

	def convert(self):

		if self.from_ is not None or self.to is not None:
			if self.currency == "₽":
				return self

			elif self.currency not in EXCHANGE_RATE:

				return Salary(self.from_, self.to, UNKNOWN_CURRENCY)	

			else:	

				rate = EXCHANGE_RATE[self.currency] 

				def to_rub(value):
					return round(value * rate) if value is not None else None

				return Salary(to_rub(self.from_), to_rub(self.to), "₽")	

		else:
			return None	



	def __repr__(self):
		return f'Salary(from_={self.from_}, to={self.to}, currency={self.currency!r})'



class Vacancy:

	def __init__(self, id, title, employer, location, experience, rating, skills, salary):
		
		self.id = id
		self.title = title
		self.employer = employer
		self.location = location
		self.experience = experience
		self.rating = rating
		self.skills = skills
		self.salary = salary

	@classmethod
	def from_dict(cls, data):

		rating = float(data['rating']) if data['rating'] else None
		salary = Salary.from_text(data['salary']) if data['salary'] else None
		if salary is not None:
			try:
				salary = salary.convert()
			except ValueError:
				salary = None

		return cls(id=int(data['id']), title=data['vacancy_name'], employer=data['company_name'], location=data['location'], experience=data['experience'], rating=rating, skills=data['skills'], salary=salary)

	def __repr__(self):
		return f'Vacancy(id={self.id}, title={self.title}, employer={self.employer}, location={self.location}, experience={self.experience}, rating={self.rating}, skills={self.skills}, salary={self.salary})'

