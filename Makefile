start:
	docker compose -f compose.yml up

scrape:
	docker compose scraper python scrape.py

crawl:
	docker compose scraper python crawl.py

.PHONY: start scrape
