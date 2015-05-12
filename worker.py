from bs4 import BeautifulSoup
from twilio.rest import TwilioRestClient

import re
import requests
import schedule
import time

 
ACCOUNT_SID = os.environ.get('ACCOUNT_SID')
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
TO_NUMBER = os.environ.get('TO_NUMBER')
FROM_NUMBER = os.environ.get('FROM_NUMBER')


def job():
    print("Sending daily message...")

    response = requests.get('https://meh.com/')

    soup = BeautifulSoup(response.text)
    item_name = re.sub(r'\s{2,}', ' ', soup.select('.features h2')[0].text.strip())
    item_image = soup.select('#gallery .photos .photo')[0]['data-src']

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(
        to=TO_NUMBER,
        from_=FROM_NUMBER,
        body='Todays meh is "{}"'.format(item_name),
        media_url=item_image,
    )


schedule.every().day.at("00:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
