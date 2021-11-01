from celery import Celery

from Scrapers.meta_factored import MetaCriticScrapter

BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
app = Celery('tasks', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)


@app.task(name='tasks.scrape')
def scrape(url, job_id):
    # url = "https://www.metacritic.com/game/pc/dota-2/user-reviews"
    chrome_driver = "./chromedriver"

    scraper = MetaCriticScrapter(url, chrome_driver)
    scraper.run()
    scraper.to_csv()
    return "Completed"
