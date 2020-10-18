import pandas as pd

pd.set_option('display.max_rows', None)


# README: this code tracks user count of ap regions
def extract_time(time):
    # Extracts the information about time in data
    date = time.split('T')[0]
    t = time.split('T')[1]
    t = t.split('.')[0]
    hour = t.split(':')[0]
    minute = t.split(':')[1]
    totalMin = int(hour) * 60 + int(minute)
    return [t, totalMin, date]

def reduce(dic):
    build = ['bryancenter-roof-ap1562d-rw-8','bryancenter-roof-ap1562d-rw-10','7791-bryancenter-roof-11','bryancenter-roof-ap1562d-rw-5','bryancenter-roof-ap1562d-rw-4','bryancenter-roof-ap1562d-rw-7','bryancenter-roof-ap1562d-rw-6','bryancenter-tkoff-ap3502i-hc-1','bryancenter-roof-ap1562d-rw-1','bryancenter-roof-ap1562d-rw-3','bryancenter-roof-ap1562d-rw-2','bryancenter-0037-ap3502i-rc-1','bryancenter-245-ap3502i-hc-1','bryanctr-mcdonalds-ap3502i-rc-1','bryancenter-305-ap3502i-rc-4','bryanctr-pg4-ap3502e-ow-1','bryancenter-303-ap3502i-rc-1','bryancenter-251-ap3502i-hc-1','bryancenter-300-ap3502i-hc-1','bryancenter-aubon-ap3502i-rc-1','bryancenter-248-ap3502i-hc-1','bryancenter-305-ap3502i-rc-2','bryancenter-104t-ap3502i-hc-1','bryancenter-243-ap3502i-hc-1','bryancenter-216-ap3502i-hc-1','bryancenter-241-ap3502i-hc-1','bryancenter-306-ap3502i-rc-1','bryancenter-246-ap3502i-hc-1','bryancenter-208-ap3502i-hc-1','bryancenter-somewhr-ap3502i-rc-1','bryancenter-339-ap3502i-rc-1','bryancenter-304-ap3502i-rc-1']
    for i in build:
        if dic[i]<0:
            dic[i] = 0
        if dic[i]>50:
            dic[i] = int(0.85*dic[i])
            continue
        if dic[i]>30:
            dic[i] = int(0.97*dic[i])
            continue
    return dic


# CHANGE PATHS ACCORDINGLY
dfData = pd.read_csv("2020_02_19.csv")
dfAps = pd.read_csv("bryan_center_aps_2019-12-10-Edited.csv")

#include connections of association type only
dfData = dfData[dfData['asa_code'].str.contains('-ASSOC')]
#delete duplicates
dfData=dfData.drop_duplicates(['_time','asa_code','macaddr','user','radiomac','slotnum','name','building_name'])

dfData.sort_values(by=["_time"], inplace=True, ascending=True)
dicCount = {ap: 0.0 for ap in dfAps['name']}
dicCount["7791-bryancenter-roof-11"] = 0
dicUser = {}
# dictionary of user to ap
minTime = 0
date = extract_time(dfData['_time'][0])[2]
dfRet = pd.DataFrame.from_dict(dicCount, orient='index')
dfRet.rename(columns={0: 'Count'}, inplace=True)
listTime = [date + ' {:02d}:{:02d}'.format(*divmod(0, 60)) for k in dicCount]
dfRet['Time'] = listTime
dfRet['minTime'] = [0 for k in dicCount]


for ind in dfData.index:
    user = dfData['user'][ind]
    ap = dfData['name'][ind]
    if ap not in dicCount:
        dicCount[ap] = 0
    #     new user scenario
    if user not in dicUser:
        dicUser[user] = ap
        dicCount[ap] += 1
    #     user moving in building
    else:
        apOld = dicUser[user]
        dicUser[user] = ap
        dicCount[apOld] -= 1
        dicCount[ap] += 1
    # executes every 5 min to print ap count values
    logMinTime = extract_time(dfData['_time'][ind])[1]
    if logMinTime > 5 + minTime:
        # reduce(dicCount)
        dfDicCount = pd.DataFrame.from_dict(dicCount, orient='index')
        dfDicCount.rename(columns={0: 'Count'}, inplace=True)
        dfDicCount.sort_values(by = ["Count"], inplace = True, ascending = False)
        minTime += 5
        listTime = [date + ' {:02d}:{:02d}'.format(*divmod(minTime, 60)) for k in dicCount]
        dfDicCount['Time'] = listTime
        dfDicCount['minTime'] = [minTime for k in dicCount]
        dfRet = dfRet.append(dfDicCount)

print(dicCount["bryancenter-roof-ap1562d-rw-8"])
dfDicCount = pd.DataFrame.from_dict(dicCount, orient='index')
dfDicCount.rename(columns={0: 'Count'}, inplace=True)
dfDicCount.sort_values(by = ["Count"], inplace = True, ascending = False)
listTime = [date + ' {:02d}:{:02d}'.format(*divmod(1439, 60)) for k in dicCount]
dfDicCount['Time'] = listTime
dfDicCount['minTime'] = [1439 for k in dicCount]
dfRet = dfRet.append(dfDicCount)

# adds index column to dfRet
dfRet = dfRet.reset_index()
dfRet.rename(columns = {'index':'ap'}, inplace = True)
dfRet = dfRet.sort_values(by = ['ap','minTime'])
dfRet = dfRet.reset_index(drop = True)
dfRet2 = dfRet.copy()

# print(dfRet)
# calculates KDE and decreases the next two intervals accordingly
test1 = 0
dfLeave = pd.read_csv("newLeavingUserCounts/LeavingUserCounts_02_19.csv")
dfLeave = dfLeave.sort_values(by = ['ap','minTime'])
dfLeave = dfLeave.reset_index(drop = True)

#The ratio part is not complete yet
lst = []
for i in range(dfRet.shape[0]-1):
    if dfRet['ap'][i] != dfRet['ap'][i+1]:
        lst.append(i)
lst.append(31210)
ratio = []
for i in range(len(lst)):
    totalCount = 0
    if i == 0:
        for j in range(lst[0]):
            count = dfLeave['Count'][j]
            totalCount += count
        if totalCount == 0:
            for k in range(lst[0]):
                ratio.append(1)
        else:
            for k in range(lst[0]):
                ratio.append(dfRet['Count'][j]/totalCount)
    else:
        for j in range(lst[i-1], lst[i]):
            count = dfLeave['Count'][j]
            totalCount += count
        if totalCount == 0:
            for k in range(lst[i]-lst[i-1]):
                ratio.append(1)
        else:
            for k in range(lst[i]-lst[i-1]):
                ratio.append(dfRet['Count'][j]/totalCount)

for ind in range(dfLeave.shape[0]):
    if dfLeave['minTime'][ind] <= 1425:
        count = dfLeave['Count'][ind]
        #filter = dfRet[dfRet['ap'] == dfLeave.at[ind, 'ap']]
        #i = filter[filter['minTime'] == (dfLeave.at[ind, 'minTime']+5)].index.values.astype(int)[0]
        #j = filter[filter['minTime'] == (dfLeave.at[ind, 'minTime']+10)].index.values.astype(int)[0]
        # print(dfRet['Count'][i])
        i = ind + 1
        test = dfRet2['Count'][i]
        while dfRet['minTime'][i] < 1439:
            dfRet['Count'][i] = dfRet['Count'][i] - (ratio[ind] * 0.81755435549 * count)
            dfRet['Count'][i+1] = dfRet['Count'][i+1] - (ratio[ind] * 0.18244564451 * count)
            i += 1
        # print(dfRet['Count'][i])
        # print("")
        """
        if dfLeave['ap'][ind] == "7791-bryancenter-roof-11":
            test1+= count
            print(count)
            print(test)
            print(dfRet['Count'][ind+1])
            print("")
        """
    elif dfLeave['minTime'][ind] == 1430:
        count = dfLeave['Count'][ind]
        #filter = dfRet[dfRet['ap'] == dfLeave.at[ind, 'ap']]
        #i = filter[filter['minTime'] == (dfLeave.at[ind, 'minTime']+5)].index.values.astype(int)[0]
        #j = filter[filter['minTime'] == 1439].index.values.astype(int)[0]
        i = ind + 1
        dfRet['Count'][i] = int(dfRet['Count'][i] - (ratio[ind] * 0.81755435549 * count))
        dfRet['Count'][i+1] = int(dfRet['Count'][j] - (ratio[ind] * 0.18244564451 * count))
    if ind%312 == 0:
        print(str(int(ind/312)) + '% done')

for ind in range(dfRet.shape[0]):
    dfRet['Count'][ind] = int(dfRet['Count'][ind])
    if dfRet['Count'][ind] < 0:
        dfRet['Count'][ind] = 0

print(test1)
# print(dfRet)
# for ind in dfDicCount.index:
#     print("'"+ind+"'" + ",")
#     if ind == ("bryancenter-304-ap3502i-rc-1"):
#         break
dfRet.to_csv("kdeCounts_02_19.csv")