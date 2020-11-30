import os
import time
from twilio.rest import Client
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup


def wscrape():
    # Send message
    account_sid = 'ACaeee2b5673a49dd89e983783e3a05b19'
    auth_token = '9c85117ecb761a410802b856a8e376ce'

    client = Client(account_sid, auth_token)

    # Scrape gambling cabin
    url = 'https://gamblingcabin.se/andelar-spela-tillsammans/'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    webpage = urlopen(req).read()
    page_soup = soup(webpage, 'html.parser')

    containers = page_soup.findAll('span','elementor-button-text')

    author_list = ['Bengan','Giganten','dybban','Vichyn']

    for container in containers:
        if any(x in str(container) for x in author_list):
            
            client.messages.create(
                to='+46760471200',
                from_='+12513094758',
                body='GTO-andelar uppe: https://gamblingcabin.se/andelar-spela-tillsammans/'
            )
            
            break

while True:
    wscrape()
    time.sleep(1800)