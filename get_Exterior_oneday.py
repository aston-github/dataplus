"""
Created on Tue July 14 2020

@author: Angela Yoon

Used to find out which aps need to be treated with the kde
"""

import pandas as pd
import glob

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

exteriorCount = {}
df = pd.read_csv("bryan_center_aps_2019-12-10-Edited.csv")
for i in range(len(df)):
    exteriorCount[extract_location(df['name'][i])] = 0

path = r'/Users/angelayoon/Documents/Duke/2020 SUMMER/Data+/8foottraffic/data'
all_files = glob.glob(path + "/*.csv")

for filename in all_files:
    df = pd.read_csv(filename)
    print(filename)
    #include connections of association type only
    df = df[df['asa_code'].str.contains('-ASSOC')]
    # delete duplicates
    df=df.drop_duplicates(['_time','asa_code','macaddr','user','radiomac','slotnum','name','building_name'])
    #sort by macaddr and break ties with time
    df = df.sort_values(by=['macaddr','_time'])
    #reassign row indices starting from 0
    df = df.reset_index(drop=True)
    print(len(df))

    #create empty dictionary allUsers
    allUsers = {}

    #assign keys and values of allUsers
    #keys are users, values are list of aps user went through
    for i in range(len(df)):
        if df['macaddr'][i] in allUsers:
            allUsers[df['macaddr'][i]].append(extract_location(df['name'][i]))
        else:
            allUsers[df['macaddr'][i]] = [extract_location(df['name'][i])]
    for user in allUsers:
        loc = allUsers[user][len(allUsers[user])-1]
        if loc not in exteriorCount:
            print(loc)
        else:
            count = exteriorCount[loc]
            exteriorCount[loc] = count+1

newDF = pd.DataFrame.from_dict(exteriorCount, orient='index')
newDF.to_csv("exterior ap count.csv")