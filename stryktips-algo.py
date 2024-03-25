from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import random
import math

def get_kupong(tipstyp):
    driver = webdriver.Chrome()

    if tipstyp == 'stryktipset':
        driver.get('https://spela.svenskaspel.se/stryktipset/')
        data = driver.find_elements(by=By.CLASS_NAME, value='stat-trend.stat-trend-neutral')
        driver.close()
    elif tipstyp == 'europatipset':
        driver.get('https://spela.svenskaspel.se/europatipset/')
        data = driver.find_elements(by=By.CLASS_NAME, value='stat-trend.stat-trend-neutral')
        driver.close()
    elif tipstyp == 'toptipset':
        driver.get('https://spela.svenskaspel.se/topptipset/')
        data = driver.find_elements(by=By.CLASS_NAME, value='stat-trend.stat-trend-neutral')
        driver.close()

    return data

def format_data(data):
    streck_list = []
    odds_list = []

    #Hämta odds och streck lista    
    for i in range(0, len(data), 3):
        if i % 2 != 0:
            #Kommer behöva konvertera från string
            odds_list.append(data[i:i+3])
        else:
            #Kommer behöva konvertera från string 
            streck_list.append(data[i:i+3])

    #Konvertera odds till % skapa lista för värde
    odds_list = [[1/item for item in odds] for odds in odds_list]
    
    #Hämta värde mellan streck och odds
    value_list = []

    for i in range(0, len(odds_list)):
        value_list.append([x - y for x,y in zip(odds_list[i], streck_list[i])])

    return value_list
    
def factorize(num):
    factors = []
    for divisor in [2, 3]:
        while num % divisor == 0:
            factors.append(divisor)
            num //= divisor
    if num > 1:
        factors.append(num)
    return factors

def combinations(num):
    factors = factorize(num)
    combinations = []
    while factors:
        combo = []
        current_product = 1
        for factor in factors:
            if current_product * factor <= num:
                combo.append(factor)
                current_product *= factor
            else:
                break
        combinations.append(combo)
        for factor in combo:
            factors.remove(factor)


    gard_dict = {'Antal halv':0, 'Antal hel':0}
    for i in combinations[0]:
        if i == 2:
            gard_dict['Antal halv'] += 1
        else:
            gard_dict['Antal hel'] += 1

    return gard_dict

def get_rader(value_list, n_rader):
    """
    1. Lista teckenvärde bäst till sämst för hela kupongen
    2. Välj ut det antal tecken som uppnår angivet pris, välj först ut grundrad och addera sedan garderingar för valt pris
    3. Kolla snitt utdelning för denna kupong
    4. Om snitt utdelningen är under vald tröskel kupongen färdig
    5. Annars ersätt det tecken med minst värde, kontrollera mot utdelnings tröskel, repetera 

    steg 5 måste testa sig fram vad som ska ersätta, om vi ersätter tecken med minst värde och uppåt kan bli problem med att bara super högoddsare kvar tillslut etc etc.
    """
    value_list = np.array(value_list)

    #1. Hitta bäst grundrad
    grund_values = np.max(value_list, axis=1)
    grund_index = np.argmax(value_list, axis=1)

    #2. Hitta bäst garderingar för angivet pris

    ## Halvgarderuingar
    n_halvgarderingar = combinations(n_rader)['Antal halv']

    sorted_indexes = np.argsort(value_list, axis=1)
    second_highest_indexes = sorted_indexes[:, -2]
    second_highest_values = value_list[np.arange(len(value_list)), second_highest_indexes]

    top_halvgarderingar_row = np.argpartition(-second_highest_values, n_halvgarderingar)[:n_halvgarderingar]
    top_halvgarderingar_col = second_highest_indexes[top_halvgarderingar_row]
    top_halvgarderingar = np.array((top_halvgarderingar_row, top_halvgarderingar_col))

    print(grund_index)
    print(top_halvgarderingar)

    ## Helgarderingar
    n_helgarderingar = combinations(n_rader)['Antal hel']
    n_helgarderingar = 2
    sorted_indexes = np.argsort(value_list[top_halvgarderingar_row], axis=1)
    third_highest_indexes = sorted_indexes[:, -3]
    third_highest_values = value_list[top_halvgarderingar_row][np.arange(len(value_list[top_halvgarderingar_row])), third_highest_indexes]

    top_helgarderingar_row = np.argpartition(-third_highest_values, n_helgarderingar)[:n_helgarderingar]
    top_helgarderingar_col = third_highest_indexes[top_helgarderingar_row]
    top_helgarderingar = np.array((top_halvgarderingar_row[top_helgarderingar_row], top_helgarderingar_col))

    print(top_helgarderingar)

    

if __name__ == '__main__':
    np.random.seed(42)

    #kupong = get_kupong('stryktipset')
    kupong = random.sample(range(1,100),78)

    value_list = format_data(kupong)
    
    array = np.random.uniform(-0.3, 0.3, size=(13, 3))
    array -= np.mean(array, axis=1, keepdims=True)
    test_value_list = np.round(array, 2)
    
    print(test_value_list) 

    antal_rader = 64
    utdelning_thresh = 100000

    get_rader(test_value_list,64)
