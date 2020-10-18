"""
Created on Fri Jun 19 22:40:12 2020

@author: Angela Yoon

Develops on markovGenerate to generate pairs of access points
Instructions:
# Enter the file path of the csv file you would like to analyze on line 39
# Enter the ap name you are interested in on line 92
# Enter the name of the csv file you would like to save the generated ranking on line 92
"""

import pandas as pd

def extract_location(location):
    #Extracts the location from full ap name
    slocation = location.split('-')
    location_list = [slocation[1]]
    location_list.append(slocation[-2]+'-'+slocation[-1])
    loc = location_list[0]+'_'+location_list[1]
    return loc

def getProcessedList(tp, df):
    #Returns a processed list of tp values from df
    if tp == 'macaddr':
        return sorted(set(df['macaddr']))
    if tp == 'user':
        return sorted(set(df['user']))
    if tp == 'location':
        locationSet = set(df['name'])
        processedLocationList = []
        for location in locationSet:
            processedLocation = extract_location(location)
            processedLocationList.append(processedLocation)
        return sorted(set(processedLocationList))

df = pd.read_csv("data/2020_02_03.csv")
#include connections of association type only
df = df[df['asa_code'].str.contains('-ASSOC')]
# delete duplicates
df=df.drop_duplicates(['_time','asa_code','macaddr','user','radiomac','slotnum','name','building_name'])
#sort by macaddr and break ties with time
df = df.sort_values(by=['macaddr','_time'])
#reassign row indices starting from 0
df = df.reset_index(drop=True)

#create empty dictionary allUsers
allUsers = {}

#assign keys and values of allUsers
#keys are users, values are list of aps user went through
for i in range(len(df)):
    if df['macaddr'][i] in allUsers:
        allUsers[df['macaddr'][i]].append(extract_location(df['name'][i]))
    else:
        allUsers[df['macaddr'][i]] = [extract_location(df['name'][i])]

#create list of all locations in df
location_list = getProcessedList('location',df)
#create new dictionary with keys as locations in location_list and values as empty lists
location_paths = {}
for location in location_list:
    location_paths[location] = []

#loop through each user
#for each location, append to location_paths[location] the pair of aps that come before and after the location
#in the form of "ap before - ap after"
#if there is no ap before or after, indicate as NA
for user in allUsers:
    if len(allUsers[user]) != 1:
        location_paths[allUsers[user][0]].append("NA - "+allUsers[user][1])
        for j in range(1,len(allUsers[user])-1):
            location_paths[allUsers[user][j]].append(allUsers[user][j-1] +" - "+ allUsers[user][j+1])
        location_paths[allUsers[user][len(allUsers[user])-1]].append(allUsers[user][len(allUsers[user])-2]+" - NA")

#generates table of most common pairs of aps that come before and after location based on datadic
#saves data in new csv file named output_file_name
def createProbabilityTable(location,datadic,output_file_name):
    location_pairs = datadic[location]
    data = {}
    for pair in location_pairs:
        if pair not in data:
            data[pair] = [1]
        else:
            data[pair][0] += 1
    new_df = pd.DataFrame.from_dict(data,orient='index')
    new_df = new_df.sort_values(by=[0],ascending=False)
    new_df.to_csv(output_file_name)