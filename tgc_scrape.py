import os
import time
from twilio.rest import Client
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup


def wscrape():
    print('Script initiated')
    # Send message
    account_sid = 'X'
    auth_token = 'X'

    client = Client(account_sid, auth_token)

    # Scrape gambling cabin
    url = 'https://gamblingcabin.se/andelar-spela-tillsammans/'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    webpage = urlopen(req).read()
    page_soup = soup(webpage, 'html.parser')

    containers = page_soup.findAll('span','elementor-button-text')

    author_list = ['Bengan','Vichyn','Dybban','dybban']

    tid = time.localtime()
    timme = tid[3]
    minut = tid[4]
    body_string = f"{timme}:{minut} https://gamblingcabin.se/andelar-spela-tillsammans/"

    for container in containers:
        if any(x in str(container) for x in author_list):
            client.messages.create(
                to='+46760471200',
                from_='+12513094758',
                body=body_string
            )
            break
            


while True:
    wscrape()
    time.sleep(30)
