bash:
	docker compose exec -it scraper bash

start:
	docker compose -f compose.yml up

scrape:
	docker compose run scraper python scrape.py

crawl:
	docker compose run scraper python crawl.py

init_db:
	docker compose run scraper python create_db.py

.PHONY: start scrape
