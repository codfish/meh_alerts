from bs4 import BeautifulSoup
from twilio.rest import TwilioRestClient

import os
import re
import redis
import requests
import schedule
import time


ACCOUNT_SID = os.environ['ACCOUNT_SID']
AUTH_TOKEN = os.environ['AUTH_TOKEN']
FROM_NUMBER = os.environ['FROM_NUMBER']


r = redis.StrictRedis(
    host=os.environ['REDIS_HOST'],
    port=os.environ['REDIS_PORT'],
    password=os.environ['REDIS_PASS'])


def job():
    print("Sending daily message...")

    response = requests.get('https://meh.com/')

    soup = BeautifulSoup(response.text)
    item_name = re.sub(r'\s{2,}', ' ', soup.select('h2')[0].text.strip())
    item_image = soup.select('#gallery .photos .photo')[0]['data-src']
    buy_button = soup.select('.buy-button')[0]
    buy_span = buy_button.find('span').extract()
    item_price = buy_button.text.strip()

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

    subscribers = r.smembers("subscribers")

    for subscriber in subscribers:
        client.messages.create(
            to=subscriber,
            from_=FROM_NUMBER,
            body='Todays meh is "{}" for {}'.format(item_name, item_price),
            media_url=item_image,
        )

schedule.every().day.at("04:01").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
