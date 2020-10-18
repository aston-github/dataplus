#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 01:02:09 2020

@author: samzhou

Estimates the coordinates of the unknown APs using regression
"""

import pandas as pd
import numpy as np
import math

def extract_location(location):
    #summarizes the location from data
    slocation = location.split('-')
    if 'bryan' not in slocation[1]:
        location_list = [slocation[1]]
    else:
        location_list = [slocation[0]]
    location_list.append(slocation[-2]+'-'+slocation[-1])
    loc = location_list[0]+'_'+location_list[1]
    return loc

df = pd.read_csv() #insert directory for a sorted list of AP locations, found in Drive

processedList = df['code']

d = {}
missing = []
notmissing = []
for i in range(103):
    if math.isnan(df['x'][i]):
        missing.append(i)
    else:
        d[i] = [int(df['floor'][i].split()[0]), int(df['x'][i]), int(df['y'][i])]
        notmissing.append(i)

df = pd.read_csv() #insert directory for markov chain, found in Box
markov = pd.DataFrame(df).to_numpy()
markov_mx = np.empty((len(missing), len(missing)), dtype=float)
for i in range(len(missing)):
    for j in range(len(missing)):
        if i == j:
            markov_mx[i][j] = -1
        else:
            markov_mx[i][j] = markov[missing[i]][missing[j]+1]
solfloor_mx = np.empty((1, len(missing)), dtype=float)
solx_mx = np.empty((1, len(missing)), dtype=float)
soly_mx = np.empty((1, len(missing)), dtype=float)
for i in range(len(missing)):
    floor = 0
    x = 0
    y = 0
    for j in range(len(notmissing)):
        coord = d[notmissing[j]]
        floor -= markov[missing[i]][notmissing[j]+1]*coord[0]
        x -= markov[missing[i]][notmissing[j]+1]*coord[1]
        y -= markov[missing[i]][notmissing[j]+1]*coord[2]
    solfloor_mx[0][i] = floor
    solx_mx[0][i] = x
    soly_mx[0][i] = y
invMarkov = np.linalg.inv(markov_mx)
floorVal = invMarkov.dot(np.transpose(solfloor_mx))
xCoord = invMarkov.dot(np.transpose(solx_mx))
yCoord = invMarkov.dot(np.transpose(soly_mx))
coordDict = {}
for i in range(len(missing)):
    if floorVal[i][0] < 1.6:
        floor = 1
    elif floorVal[i][0] < 2.4:
        floor = 2
    else:
        floor = 3
    coordDict[processedList[missing[i]]] = [floor, int(xCoord[i][0]), int(yCoord[i][0])]
headers = ['floor', 'x', 'y']
coord = pd.DataFrame.from_dict(coordDict, orient='index', columns = headers)
pd.DataFrame(coord).to_csv() #insert new directory for the csv containing estimates coordinates

