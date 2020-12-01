from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np

driver = webdriver.Chrome('chromedriver')
driver.get('https://spela.svenskaspel.se/europatipset/')
data = driver.find_elements_by_xpath('//div[@class="statistics-box"]')



for i in range(0,6*13 + 1):
    for j in range(0,3):
        print(i)

driver.close()
