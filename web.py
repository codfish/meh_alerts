from flask import Flask, render_template, request, flash, redirect, url_for
from pprint import pprint
from twilio.rest import TwilioRestClient
from twilio import twiml

import datetime
import os
import redis
import requests


ACCOUNT_SID = os.environ['ACCOUNT_SID']
AUTH_TOKEN = os.environ['AUTH_TOKEN']
FROM_NUMBER = os.environ['FROM_NUMBER']


app = Flask(__name__)
r = redis.StrictRedis(
    host=os.environ['REDIS_HOST'],
    port=os.environ['REDIS_PORT'],
    password=os.environ['REDIS_PASS'])
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


@app.route("/")
def home():
    twilio_payload = r.get('twilio_payload')
    return render_template('home.html', twilio_payload=twilio_payload)


@app.route("/subscribe/", methods=['POST'])
def subscribe():
    is_human = requests.post("https://www.google.com/recaptcha/api/siteverify", data={
        'secret': os.environ['RECAPTCHA_SECRET'],
        'response': request.form['g-recaptcha-response'],
    }).json()['success']

    if is_human:
        client.messages.create(
            to=request.form['phone'],
            from_=FROM_NUMBER,
            body='Reply with the word MEH to confirm your subscription.  You may unsubscribe at any time by replying with the word STOP.'
        )

        flash("Your almost done.  Check your phone for a message from us.")
    else:
        flash("Go away ROBOT!")

    return redirect(url_for('home'))


@app.route("/message/", methods=['POST'])
def read_message():
    r.set('twilio_payload', pprint(request))
    resp = twilio.twiml.Response()
    resp.message("Hello, Mobile Monkey")
    return str(resp)


if __name__ == "__main__":
    app.debug = True
    app.secret_key = os.environ['SECRET_KEY']

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
