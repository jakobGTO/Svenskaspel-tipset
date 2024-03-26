from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import matplotlib.pyplot as plt
from scipy.stats import normaltest
import pandas as pd
import numpy as np
import random
import math

def get_kupong(tipstyp):
    driver = webdriver.Chrome()

    if tipstyp == 'stryktipset':
        driver.get('https://spela.svenskaspel.se/stryktipset/')
        data = driver.find_elements(by=By.CLASS_NAME, value='stat-trend.stat-trend-neutral')
        return data

    elif tipstyp == 'europatipset':
        driver.get('https://spela.svenskaspel.se/europatipset/')
        data = driver.find_elements(by=By.CLASS_NAME, value='stat-trend.stat-trend-neutral')
        return data
    elif tipstyp == 'toptipset':
        driver.get('https://spela.svenskaspel.se/topptipset/')
        data = driver.find_elements(by=By.CLASS_NAME, value='stat-trend.stat-trend-neutral')
        return data

    driver.close()

    #return data

def format_data(data):
    streck_list = []
    odds_list = []
    new_data = []

    for text in data:
        new_data.append(text.text)

    #Hämta odds och streck lista    
    for i in range(0, len(new_data), 3):
        if i % 2 != 0:
            #Kommer behöva konvertera från string
            odds_list.append(new_data[i:i+3])
        else:
            #Kommer behöva konvertera från string 
            streck_list.append(new_data[i:i+3])

    streck_list = [[float(streck.strip('%')) / 100 for streck in inner_list] for inner_list in streck_list]
    odds_list = [[float(odds.replace(',', '.')) for odds in inner_list] for inner_list in odds_list]

    #Konvertera odds till % skapa lista för värde
    odds_list = [[1/item for item in odds] for odds in odds_list]

    #print(streck_list, '\n')
    #print(odds_list, '\n')

    #Hämta värde mellan streck och odds
    value_list = []

    for i in range(0, len(odds_list)):
        value_list.append([x - y for x,y in zip(odds_list[i], streck_list[i])])

    #print(value_list)

    return value_list, odds_list, streck_list
    
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

def get_risk(streck_list):
    streck_list = np.array(streck_list)
    min_risk = np.argmax(streck_list, axis=1)
    max_risk = np.argmin(streck_list, axis=1)
    
    min_risk_list = []
    max_risk_list = []

    for i,row in enumerate(min_risk):
        min_risk_list.append(streck_list[i, row])

    for j,row in enumerate(max_risk):
        max_risk_list.append(streck_list[j, row])

    minrisk_median = np.median(min_risk_list)
    maxrisk_median = np.median(max_risk_list)

    interval_width = (minrisk_median + maxrisk_median) / 2
    threshold_list = [maxrisk_median, interval_width, minrisk_median]

    return threshold_list

def get_rader(value_list, streck_list, risk_level, n_rader, viz):
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
    grund_index = np.vstack((np.arange(13),np.argmax(value_list, axis=1)))

    #2. Hitta bäst garderingar för angivet pris

    ## Halvgarderuingar
    n_halvgarderingar = combinations(n_rader)['Antal halv']
    n_helgarderingar = combinations(n_rader)['Antal hel']
    n_halvgarderingar = n_halvgarderingar + n_helgarderingar


    sorted_indexes = np.argsort(value_list, axis=1)
    second_highest_indexes = sorted_indexes[:, -2]
    second_highest_values = value_list[np.arange(len(value_list)), second_highest_indexes]

    top_halvgarderingar_row = np.argpartition(-second_highest_values, n_halvgarderingar)[:n_halvgarderingar]
    top_halvgarderingar_col = second_highest_indexes[top_halvgarderingar_row]
    top_halvgarderingar = np.array((top_halvgarderingar_row, top_halvgarderingar_col))

    #print(grund_index)
    #print(top_halvgarderingar)

    ## Helgarderingar
    sorted_indexes = np.argsort(value_list[top_halvgarderingar_row], axis=1)
    third_highest_indexes = sorted_indexes[:, -3]
    third_highest_values = value_list[top_halvgarderingar_row][np.arange(len(value_list[top_halvgarderingar_row])), third_highest_indexes]

    top_helgarderingar_row = np.argpartition(-third_highest_values, n_helgarderingar)[:n_helgarderingar]
    top_helgarderingar_col = third_highest_indexes[top_helgarderingar_row]
    top_helgarderingar = np.array((top_halvgarderingar_row[top_helgarderingar_row], top_helgarderingar_col))

    #print(top_helgarderingar)

    viz_array = np.full((13,3), ".", dtype='<U1')
    viz_array[grund_index[0], grund_index[1]] = 'X'
    viz_array[top_halvgarderingar[0], top_halvgarderingar[1]] = 'X'
    viz_array[top_helgarderingar[0], top_helgarderingar[1]] = 'X'

    res_array = np.zeros((13,3))
    res_array[grund_index[0], grund_index[1]] = 1
    res_array[top_halvgarderingar[0], top_halvgarderingar[1]] = 1
    res_array[top_helgarderingar[0], top_helgarderingar[1]] = 1

    if viz == True:
        for i,row in enumerate(viz_array):
            print(i+1, row)

    streck_list = np.array(streck_list)
    streck_list = np.concatenate((streck_list[grund_index[0], grund_index[1]], streck_list[top_halvgarderingar[0], top_halvgarderingar[1]], streck_list[top_helgarderingar[0], top_helgarderingar[1]]))
    
    print('Streck värden')
    print("Mean:", np.mean(streck_list))
    print("Median:", np.median(streck_list))
    print("Standard Deviation:", np.std(streck_list))
    print("Minimum:", np.min(streck_list))
    print("Maximum:", np.max(streck_list))

    return res_array

if __name__ == '__main__':
    np.random.seed(42)

    kupong = get_kupong('stryktipset')
    value_list, odds_list, streck_list = format_data(kupong)

    #hög risk = [0, risk_thresholds[0]]
    #medium hög = [risk_thresholds[0], risk_thresholds[1]]
    #medium låg = [risk_thresholds[1], risk_thresholds[2]]
    #låg = [risk_thresholds[2], 1]
    risk_thresholds = get_risk(streck_list = streck_list)


    get_rader(value_list = value_list, 
                streck_list = streck_list,
                risk_level = 'high',
                n_rader=288,
                viz=True)
    