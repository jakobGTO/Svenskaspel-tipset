from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import matplotlib.pyplot as plt
from scipy.stats import normaltest
import pandas as pd
import numpy as np
import random
import math
from itertools import product
from collections import defaultdict

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

    prob_list = [[1/item for item in odds] for odds in odds_list]

    #print(streck_list, '\n')
    #print(odds_list, '\n')

    #Hämta värde mellan streck och odds
    value_list = []

    for i in range(0, len(odds_list)):
        value_list.append([x - y for x,y in zip(prob_list[i], streck_list[i])])

    #print(value_list)

    return value_list, odds_list, streck_list
        
def risk_levels(odds_grid):
    odds_grid = np.array(odds_grid)
    
    # Genererar alla olika kombinationer av enkel rader
    all_combinations = list(product(range(3), repeat=13))
    
    # Beräknar totala odds för alla rad kombos
    total_odds = [np.prod([odds_grid[i, combo[i]] for i in range(13)]) for combo in all_combinations]
    
    # Index med lägst och högst odds
    highest_odds_index = np.argmax(total_odds)
    lowest_odds_index = np.argmin(total_odds)

    # Hitta högst och lägst odds, dela upp i 4 nivåer
    highest_odds = total_odds[highest_odds_index]
    lowest_odds = total_odds[lowest_odds_index]

    range_value = highest_odds - lowest_odds
    quartile_size = range_value / 4

    quartiles = {
        "low risk":(lowest_odds, lowest_odds + quartile_size),
        "medium-low risk":(lowest_odds + quartile_size, lowest_odds + 2 * quartile_size),
        "medium-high risk":(lowest_odds + 2 * quartile_size, lowest_odds + 3 * quartile_size),
        "high risk":(lowest_odds + 3 * quartile_size, highest_odds)
    }

    return quartiles

def select_optimal_tickets(value_list, odds_list, number_of_tickets, risk_level, risk_levels):
    value_array = np.array(value_list)
    odds_array = np.array(odds_list)
    
    # Genererar alla olika kombinationer av enkel rader
    all_combinations = list(product(range(3), repeat=13))

    # Beräknar totala värdet och odds för varje rad
    combination_values = []
    combination_odds = []
    for combo in all_combinations:
        value = sum(value_array[i, combo[i]] for i in range(13))
        odds = np.prod([odds_array[i, combo[i]] for i in range(13)])
        combination_values.append(value)
        combination_odds.append(odds)
    
    # Sorterar för rader med högst värde
    sorted_indices = np.argsort(combination_values)[::-1]
    
    # Väljer de med högst värde upp till antal rader vi vill ha
    selected_tickets = sorted_indices[:number_of_tickets]
    
    # Hittar min och max risk
    min_risk, max_risk = risk_levels[risk_level]
    
    # Justerar rader för att hamna inom risk nivå
    max_iterations = 1_000_000
    for _ in range(max_iterations):
        average_odds = np.mean([combination_odds[i] for i in selected_tickets])
        
        if min_risk <= average_odds <= max_risk:
            break
        
        if average_odds > max_risk:
            # Byt ut raden med lägst värde med den rad med högst värde vi ännu inte testat
            lowest_value_index = min(selected_tickets, key=lambda x: combination_values[x])
            for i in sorted_indices:
                if i not in selected_tickets and combination_odds[i] < combination_odds[lowest_value_index]:
                    selected_tickets.remove(lowest_value_index)
                    selected_tickets.append(i)
                    break
    else:
        print("Vi har fastnat")
    
    selected_combinations = [all_combinations[i] for i in selected_tickets]
    
    return selected_combinations, average_odds

def combination_to_string(combo):
    return ','.join(['1' if x == 0 else 'X' if x == 1 else '2' for x in combo])

if __name__ == '__main__':
    kupong = get_kupong('stryktipset')
    value_list, odds_list, streck_list = format_data(kupong)
    risk_level = risk_levels(odds_list)
    number_of_tickets = 256
    selected_risk_level = 'low risk'
    
    optimal_tickets, average_odds = select_optimal_tickets(value_list, odds_list, number_of_tickets, selected_risk_level, risk_level)

    output_lines = ["Stryktipset"]  
    for i, ticket in enumerate(optimal_tickets, 1):
        ticket_str = f"E,{combination_to_string(ticket)}"
        output_lines.append(ticket_str)
        #print(ticket_str)

    file_path = "D:/enkla_rader.txt"
    with open(file_path, 'w') as f:
        f.write('\n'.join(output_lines))
