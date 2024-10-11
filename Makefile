bash:
	docker compose exec -it scraper bash

start:
	docker compose -f compose.yml up

scrape:
	docker compose scraper python scrape.py

crawl:
	docker compose scraper python crawl.py

init_db:
	docker compose scraper python create_db.py

.PHONY: start scrape
