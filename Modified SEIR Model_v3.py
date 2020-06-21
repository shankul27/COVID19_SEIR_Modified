#!/usr/bin/env python
# coding: utf-8

# In[44]:


import numpy as np
import pandas as pd
import requests
import json
from datetime import datetime
from datetime import timedelta 
pd.options.mode.chained_assignment = None  # default='warn'


# In[45]:


#added a new variable Iso to take into account those patients who got isolated
def modified_seir_model(init_vals, params, t):
    S_0, E_0, I_0, Iso_0, R_0 = init_vals
    S, E, I, Iso, R = [S_0], [E_0], [I_0],[Iso_0], [R_0]
    Total = [Iso_0+R_0]
    alpha, beta, gamma, delta = params
    dt = t[1] - t[0]
    
    for _ in t[1:]:            
        next_S = S[-1] - (beta*S[-1]*I[-1])*dt
        next_E = E[-1] + (beta*S[-1]*I[-1] - alpha*E[-1])*dt
        next_I = I[-1] + (alpha*E[-1] - gamma*I[-1])*dt
        next_Iso = Iso[-1] + (gamma*I[-1]- delta*Iso[-1])*dt
        next_R = R[-1] + (delta*Iso[-1])*dt
        S.append(next_S)
        E.append(next_E)
        I.append(next_I)
        Iso.append(next_Iso)
        R.append(next_R)
        Total.append(next_Iso+next_R)
    return np.stack([S, E, I, Iso, R, Total]).T


# In[46]:


state = 'mh' #a different state can be selected based on its state code
day_zero = datetime(2020, 4, 3) #1st day from which calculation starts

# Update value of N with the total population for the state. Population of a few states is already mentioned below
#N = 1352600000 #india
#N = 64801901 #gujrat
#N = 37960000 #kerela
#N = 233378519 #UP
N = 67000000 #karnataka

numOfDays = 60 # num of days for which prediction has to made


# In[47]:


#calling covid19india API to retrieve adata 
url = 'https://api.covid19india.org/states_daily.json'
response = requests.get(url)
content = json.loads(response.text)
records = content['states_daily']
rawDataframe = pd.DataFrame.from_records(records) #recieved data converted to dataframes

#filtered data for the mentioned state
filteredDataframe = rawDataframe[['date', 'status', state]]


# In[48]:


#Data Cleaning and rearrangement
dataframe = pd.pivot(data = filteredDataframe, index = 'date', columns = 'status', values = state)
dataframe.index = pd.to_datetime(dataframe.index)
dataframe.sort_values(by=['date'], inplace=True)
for column in dataframe:
    dataframe[column] = dataframe[column].astype(int)
    dataframe['Total ' + column] = dataframe[column].cumsum()
dataframe['date'] = dataframe.index
dataframe = dataframe[dataframe['date'] >= day_zero]
dataframeCopy = dataframe.copy()
dataframe.index = np.arange(0, len(dataframe))


# In[49]:


#Get initial vales for Infected, Exposed, Recovered and Confired cases from the downloaded data
a = pd.read_excel('E and I Template.xlsx')

initiallyInfected = (a['Infective Distribution']*dataframe['Confirmed'][:len(a)]).sum()
print('Initially Infected: ' + str(initiallyInfected))

initiallyExposed = (a['Exposed Distribution']*dataframe['Confirmed'][:len(a)]).sum()
print('Initially Exposed: ' + str(initiallyExposed))

initiallyRecoveredDead =  dataframe['Total Recovered'][0] + dataframe['Total Deceased'][0]
print('Initially Recovered or Dead: ' + str(initiallyRecoveredDead))

initiallyInfectedDetected = dataframe['Total Confirmed'][0] - initiallyRecoveredDead
print('Initially Infected Detected: ' + str(initiallyInfectedDetected))


# In[50]:


# Define parameters to derive alpha, beta, gamma and delta

isolationPeriod = 15 # Average No. of days after which patient is declared Recovered or Dead 
cureOrDetectionPeriod = 6
incubationPeriod = 5.2 #5.2 #https://annals.org/aim/fullarticle/2762808/incubation-period-coronavirus-disease-2019-covid-19-from-publicly-reported
#covidMortality = 0.002 #https://www.worldometers.info/coronavirus/coronavirus-death-rate/#who-03-03-20 

init_vals = (N - (initiallyExposed + initiallyInfected + initiallyInfectedDetected + initiallyRecoveredDead))/N, initiallyExposed/N, initiallyInfected/N,initiallyInfectedDetected/N, initiallyRecoveredDead/N

#Derive alpha,, gamma, delta values
alpha = 1/incubationPeriod
gamma = 1/cureOrDetectionPeriod
delta = 1/isolationPeriod


# In[51]:


#limits of the simulation loop
t_max = numOfDays
dt = .1
t = np.linspace(0, t_max, int(t_max/dt) + 1)

#limit for R value. Taken from 0.75 to 4
loopRange = np.arange(0.75,4.25,0.25)

#initialize empty datasets
final_Dataset = pd.DataFrame()
final_Dataset_Total = pd.DataFrame()
final_Dataset_Active = pd.DataFrame()
final_Dataset_New = pd.DataFrame()


# In[52]:


# Run simulation

#this loop is for each value of beta
for i in loopRange:
    beta = i/cureOrDetectionPeriod #beta calculated by R value
    
    params = alpha, beta, gamma, delta
    results = modified_seir_model(init_vals, params, t) #modified SEIR model
    
    #data rearrangement
    dataset = pd.DataFrame(results*N)
    dataset = dataset[dataset.index % 10 == 0]
    dataset.columns = ['Susceptible Cases (R='+ str(i)+')','Exposed Cases (R='+ str(i)+')','Infectious Cases (R='+ str(i)+')', 'Active Cases (R='+ str(i)+')','Recovered/Dead Cases (R='+ str(i)+')','Total Cases (R='+ str(i)+')']
    
    #Add values to parent dataset
    final_Dataset = pd.concat([final_Dataset, dataset],axis=1)
    final_Dataset_Total = pd.concat([final_Dataset_Total, dataset['Total Cases (R='+ str(i)+')']],axis=1)
    final_Dataset_Active = pd.concat([final_Dataset_Active,dataset['Active Cases (R='+ str(i)+')']],axis=1)
    final_Dataset_New = pd.concat([final_Dataset_New,dataset['Active Cases (R='+ str(i)+')']],axis=1)
    final_Dataset_New = pd.concat([final_Dataset_New,dataset['Recovered/Dead Cases (R='+ str(i)+')']],axis=1)


# In[53]:


#calculating each day value by simple subtraction of cumulative values
for i in np.arange(1,len(final_Dataset_New)):
    final_Dataset_New.iloc[i-1] = final_Dataset_New.iloc[i] - final_Dataset_New.iloc[i-1]
for i in loopRange:
    final_Dataset_New['Active Cases (R='+ str(i)+')'] = final_Dataset_New['Active Cases (R='+ str(i)+')'] + final_Dataset_New['Recovered/Dead Cases (R='+ str(i)+')']
    del final_Dataset_New['Recovered/Dead Cases (R='+ str(i)+')']


# In[54]:


#datetime manipulation and updating index with date value
days = pd.date_range(day_zero, day_zero + timedelta(numOfDays), freq='D')
final_Dataset.index = days
final_Dataset_Total.index = days
final_Dataset_Active.index = days
final_Dataset_New.index = days
final_Dataset_Total = pd.concat([dataframeCopy['Total Confirmed'],final_Dataset_Total],axis=1)
final_Dataset_Active = pd.concat([dataframeCopy['Total Confirmed'] - dataframeCopy['Total Deceased'] - dataframeCopy['Total Recovered'],final_Dataset_Active],axis=1)
final_Dataset_New = pd.concat([dataframeCopy['Confirmed'],final_Dataset_New],axis=1)
final_Dataset_New = final_Dataset_New[:-1]


# In[35]:


#Save dataset to an excel file on local drive
now = datetime.now()
final_Dataset.to_excel (r'C:\Users\Manjul\Downloads\COVID-19\\' + now.strftime("%d-%m %H%M") + " " + state + " " + day_zero.strftime("%d-%m") +  ' Raw File.xls', index = True)
final_Dataset_Total.to_excel (r'C:\Users\Manjul\Downloads\COVID-19\\' + now.strftime("%d-%m %H%M") + " " + state + " " + day_zero.strftime("%d-%m") +  ' Total Cases.xls', index = True)
final_Dataset_Active.to_excel (r'C:\Users\Manjul\Downloads\COVID-19\\' + now.strftime("%d-%m %H%M") + " " + state + " " + day_zero.strftime("%d-%m") +  ' Active Cases.xls', index = True)
final_Dataset_New.to_excel (r'C:\Users\Manjul\Downloads\COVID-19\\' + now.strftime("%d-%m %H%M") + " " + state + " " + day_zero.strftime("%d-%m") +  ' New Cases.xls', index = True)


# In[ ]:




