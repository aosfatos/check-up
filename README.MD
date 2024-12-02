
# Check-up
![cover](https://raw.githubusercontent.com/aosfatos/check-up/refs/heads/develop/cover.png)  
Check-up is a project aimed at analyzing the presence of misinformation in health ads that are promoted on major news websites in Brazil.

This repository contains the code for a tool developed by [**Aos Fatos**](https://aosfatos.org) to examine native ads from ten news websites (listed below).

The tool has three modules: a crawler that collects links from each site, a scraper that captures and archives found advertisements, and an ad classifier by theme using a large language model (LLM).

Although it only works with the ten sites covered by the project, this code can easily be adapted for use on other websites, as demonstrated below.

The code for this project may only be used for non-commercial purposes and with proper attribution.

## News Portals
This repository initially includes news collection from the following portals:

- [Estadão](https://www.estadao.com.br)
- [Folha](https://www.folha.uol.com.br)
- [Globo](https://oglobo.globo.com/)
- [IG](https://www.ig.com.br)
- [Metrópoles](https://www.metropoles.com)
- [R7](https://www.r7.com)
- [RBS](https://www.clicrbs.com.br)
- [Terra](https://www.terra.com.br)
- [Veja](https://veja.abril.com.br)
- [UOL](https://www.uol.com.br)

## Script Execution

### Start Services

To start the required services, use the command:

`make start`

This command launches a Docker container with a database and a shell container with Python installed.

### 1- Initialize the Database Tables
To create the necessary tables, execute:

`make init_db`

The following tables will be created:

- Portal: Information about the analyzed portals.
- Entry: News articles collected from each portal.
- Advertisement: Ads found in the news articles.
- URLQueue: Queue of URLs for the scraping process.
- QueueStatus: Status of each scraping queue.

**Note:** More details about the table structure are available in the `models.py` file.

### 2- Collect News URLs
The first step is to collect URLs of news articles from the portals' homepages. Each portal has a "spider" implemented using the Scrapy library, located in the `spiders/` directory.

Example script for [Folha]("https://www.folha.uol.com.br"): `spiders/folha.py`.

To collect URLs from all portals, use:

`make crawl`

### 3- Collect Ad Information

After collecting news articles, the next step is to scrape ads present on the news pages. This process uses the [Playwright](https://playwright.dev/) library to simulate browser navigation.

To collect ads from all portals, execute:

`make scrape`

### 4- Add a New Portal

#### 4.1 - Add a New Portal to the Database
To add a new portal, such as [Correio Braziliense](https://www.correiobraziliense.com.br/), insert the portal's information into the database:

```
make bash

python add_portal.py "Correio Braziliense" "https://www.correiobraziliense.com.br/"
```

#### 4.2 - Create the Spider
Create a file `spiders/correio.py` with the following content:

```python
import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem

class CorreioBrazilienseSpider(BaseSpider):
    name = "correiobraziliensespider"
    start_urls = ["https://www.correiobraziliense.com.br/"]
    allowed_domains = ["correiobraziliense.com.br"]

    def allow_url(self, entry_url):
        return "https://correiobraziliense.com.br" in entry_url

    def parse(self, response):
        url_item = URLItem()
        for entry in response.css('a[title][data-tb-link]::attr(href)'):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                url_item["url"] = url
                yield url_item
                yield scrapy.Request(url=url, callback=self.parse)
```

This script will fetch new articles published on Correio Braziliense's homepage.

#### 4.3 - Create the Playwright Script
You will also need to create a corresponding Playwright script for the new portal to collect ads. Create a file in `plays/correio.py` with the following code:

```python
import time

from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import AdItem, EntryItem
from plays.utils import get_or_none
from plog import logger

class CorreioBraziliensePlay(BasePlay):
    name = "correiobraziliense"
    n_expected_ads = 10  # Add the minimum amount of expected ads

    @classmethod
    def match(cls, url):
        return "correiobraziliense.com.br" in url

    def find_items(self, html_content) -> AdItem:
        return AdItem(
            title=get_or_none(r'title="(.*?)"', html_content),
            url=get_or_none(r'href="(.*?)"', html_content),
            thumbnail_url=get_or_none(r'url\(&quot;(.*?)&quot;\)', html_content),
            tag=get_or_none(r'<span class="branding-inner".*?>(.*?)<\/span>', html_content),
        )

    def pre_run(self):
        pass

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)
            logger.info(f"[{self.name}] Searching for ads...")
            page.locator("#taboola-below-article-thumbnails").scroll_into_view_if_needed()

            entry_screenshot_path = self.take_screenshot(page, self.url, goto=False)
            entry_title = page.locator("title").inner_text()
            time.sleep(self.wait_time * 2)

            elements = page.locator(".videoCube")
            ad_items = []
            visible_elements = []
            for i in range(elements.count()):
                element = elements.nth(i)
                if not element.is_visible():
                    continue
                visible_elements.append(element)
                content = element.inner_html()
                ad_item = self.find_items(content)
                ad_items.append(ad_item)

            return EntryItem(
                title=entry_title,
                ads=ad_items,
                url=self.url,
                screenshot_path=entry_screenshot_path,
            )
```

This script will search for native ads in the articles collected from the Correio Braziliense portal.

**Note:** The `run` method is responsible for searching ads in the site's HTML structure. It should be developed according to each portal's structure.

## Ad Classification with LLM
Each collected ad is classified into one of the 45 categories described in `llm/categories.py`. This classification is optional. To activate it, simply add your OpenAI API key to the `OPENAI_API_KEY` variable.  
For more information, visit the [OpenAI](https://platform.openai.com/docs/api-reference/api-keys) site.

## File Storage
During ad collection, the script simulating the browser will record screenshots of the portals' news pages and the ad pages.

To store these images, configure an [S3 Bucket](https://aws.amazon.com/s3/) on Amazon Web Services (AWS) and update the access credentials in the `.env` file with the following parameters:

- **AWS_ACCESS_KEY_ID**
- **AWS_SECRET_ACCESS_KEY**
- **AWS_S3_REGION_NAME**
- **AWS_BUCKET_NAME**

The S3 addresses of the images will be recorded in the project's database, while the image files will be stored in the configured bucket.

## Important
The scripts depend on the portals' HTML structure and may need adjustments after website updates.
