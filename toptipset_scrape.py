from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np
import openpyxl


driver = webdriver.Chrome('chromedriver')
driver.get('https://spela.svenskaspel.se/topptipset/')
data = driver.find_elements_by_xpath('//div[@class="statistics-box"]')
team_names = driver.find_elements_by_xpath('//span[@class="f-550 js-match match-header"]')

data_list = []
for rows in data:
    data_list.append(rows.text)


df_array = []
x=0
y=3
for i in range(8*2):
    df_array.append(data_list[x:y])
    x += 3
    y += 3

df_teams_array = []
for i in range(8):
    df_teams_array.append(team_names[i].text)


str_list = [i for i in reversed(df_array[::-2])]

df_str = pd.DataFrame(data=str_list,columns = ['1_str','X_str','2_str'])
df_odds = pd.DataFrame(data=df_array[::2],columns = ['1_odds','X_odds','2_odds'])
df_names = pd.DataFrame(data=df_teams_array,columns = ['Teams'])

df_master = pd.concat([df_names,df_odds,df_str],axis=1,ignore_index=True)

df = df_master.rename(columns={0:'Teams',1:'1_odds',2:'X_odds',3:'2_odds',4:'1_str',5:'X_str',6:'2_str'})

df['1_str'] = df['1_str'].str.rstrip('%').astype('float')/100.0
df['X_str'] = df['X_str'].str.rstrip('%').astype('float')/100.0
df['2_str'] = df['2_str'].str.rstrip('%').astype('float')/100.0

for i in range(8):
    df.loc[i,'1_odds'] = float(str(df.loc[i,'1_odds']).replace(',','.'))
    df.loc[i,'X_odds'] = float(str(df.loc[i,'X_odds']).replace(',','.'))
    df.loc[i,'2_odds'] = float(str(df.loc[i,'2_odds']).replace(',','.'))

df['1 Över/Understreckning (+/-)'] = np.nan
df['X Över/Understreckning (+/-)'] = np.nan
df['2 Över/Understreckning (+/-)'] = np.nan

for i in range(8):
    df.iloc[i,7] = ((df.loc[i,'1_str']) - (df.loc[i,'1_odds'] ** -1)) * 100
    df.iloc[i,8] = ((df.loc[i,'X_str']) - (df.loc[i,'X_odds'] ** -1)) * 100
    df.iloc[i,9] = ((df.loc[i,'2_str']) - (df.loc[i,'2_odds'] ** -1)) * 100


df.to_excel('Topptipset.xlsx',sheet_name = 'Sheet_name_1')

driver.close()

