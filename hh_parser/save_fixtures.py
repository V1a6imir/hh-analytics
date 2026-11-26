from hh_parser.clients.sync_client import HHClient

with HHClient() as client:

	page = client.get_search_page('developer')
	with open('tests/fixtures/search_page.html', 'w', encoding='utf-8') as f:
		f.write(page)

	vacancy_with_skills = client.get_vacancy_page('139322064')
	with open('tests/fixtures/vacancy_with_skills.html', 'w', encoding='utf-8') as f:
		f.write(vacancy_with_skills)
	
	vacancy_without_skills = client.get_vacancy_page('135584548')
	with open('tests/fixtures/vacancy_without_skills.html', 'w', encoding='utf-8') as f:
		f.write(vacancy_without_skills)
