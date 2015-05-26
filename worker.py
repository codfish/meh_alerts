from bs4 import BeautifulSoup
from twilio.rest import TwilioRestClient, exceptions as twilio_exceptions
from apiclient.discovery import build

import os
import re
import redis
import requests
import schedule
import time


ACCOUNT_SID = os.environ['ACCOUNT_SID']
AUTH_TOKEN = os.environ['AUTH_TOKEN']
FROM_NUMBER = os.environ['FROM_NUMBER']
GOOGL_API_KEY = os.environ['GOOGL_API_KEY']


r = redis.StrictRedis(
    host=os.environ['REDIS_HOST'],
    port=os.environ['REDIS_PORT'],
    password=os.environ['REDIS_PASS'])


def url(link):
    service = build('urlshortener', 'v1', developerKey=GOOGL_API_KEY)
    url = service.url()
    body = {'longUrl': link}
    response = url.insert(body=body).execute()
    return response['id']

def job():
    print("Sending daily message...")

    response = requests.get('https://meh.com/')

    soup = BeautifulSoup(response.text)
    item_name = re.sub(r'\s{2,}', ' ', soup.select('h2')[0].text.strip())
    item_image = soup.select('#gallery .photos .photo')[0]['data-src']
    buy_button = soup.select('.buy-button')[0]
    buy_span = buy_button.find('span').extract()
    item_price = buy_button.text.strip()
    item_link = soup.select('[rel="canonical"]')[0]['href']
    short_link = url(item_link)

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

    subscribers = r.smembers("subscribers")

    for subscriber in subscribers:
        try:
            client.messages.create(
                to=subscriber,
                from_=FROM_NUMBER,
                body='Todays meh is "{}" for {} {}'.format(item_name, item_price, short_link),
                media_url=item_image,
            )
        except twilio_exceptions.TwilioRestException:
            print("Error sending message to {}".format(subscriber))

schedule.every().day.at("04:01").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
