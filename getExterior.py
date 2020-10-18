"""
Created on Wed Jun 24 2020

@author: Angela Yoon

Used to find out the most common exterior aps
Derives several functions from markovGenerate
"""

import pandas as pd

def extract_location(location):
    #Summarizes the location from data
    slocation = location.split('-')
    if 'bryan' not in slocation[1]:
        location_list = [slocation[1]]
    else:
        location_list = [slocation[0]]
    location_list.append(slocation[-2]+'-'+slocation[-1])
    loc = location_list[0]+'_'+location_list[1]
    return loc

def getLocationList(df):
    # Returns a processed list of locations from df
    locationSet = set(df['name'])
    processedLocationList = []
    for location in locationSet:
        processedLocation = extract_location(location)
        processedLocationList.append(processedLocation)
    return sorted(set(processedLocationList))

df = pd.read_csv("data/2020_02_03.csv")
#include connections of association type only
df = df[df['asa_code'].str.contains('-ASSOC')]
#sort by macaddr and break ties with time
df = df.sort_values(by=['macaddr','_time'])
#reassign row indices starting from 0
df = df.reset_index(drop=True)

#create empty dictionary entering_exterior and exiting_exterior
entering_exterior = {}
exiting_exterior = {}

#treat first row separately
entering_exterior[extract_location(df['name'][0])]=1

for i in range(len(df)-1):
    if df['macaddr'][i] != df['macaddr'][i+1]:
        exit = extract_location(df['name'][i])
        enter = extract_location(df['name'][i+1])
        if exit not in exiting_exterior:
            exiting_exterior[exit] = 0
        exiting_exterior[exit] += 1
        if enter not in entering_exterior:
            entering_exterior[enter] = 0
        entering_exterior[enter] += 1

#treat last row separately
last_exit = extract_location(df['name'][len(df)-1])
if last_exit not in exiting_exterior:
    exiting_exterior[exit] = 0
exiting_exterior[exit] += 1

exittotal=0
entertotal=0
for exit in exiting_exterior:
    exittotal += exiting_exterior[exit]
for enter in entering_exterior:
    entertotal += entering_exterior[enter]

dic = {}
locationSet = getLocationList(df)
dic[enter] = []
dic[exit] = []
for location in locationSet:
    if location not in entering_exterior:
        dic[enter].append(0)
    else:
        dic[enter].append(entering_exterior[location]/entertotal)
    if location not in exiting_exterior:
        dic[exit].append(0)
    else:
        dic[exit].append(exiting_exterior[location] / exittotal)

new_df=pd.DataFrame(dic,columns=['enter','exit'],index=list(locationSet))
new_df.to_csv("exterior aps with probability")