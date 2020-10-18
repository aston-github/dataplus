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
dfData = pd.read_csv("data/2020_02_19.csv")
dfAps = pd.read_csv("bryan_center_aps_2019-12-10-Edited.csv")

#include connections of association type only
dfData = dfData[dfData['asa_code'].str.contains('-ASSOC')]
#delete duplicates
dfData=dfData.drop_duplicates(['_time','asa_code','macaddr','user','radiomac','slotnum','name','building_name'])

dfData.sort_values(by=["_time"], inplace=True, ascending=True)
dicCount = {ap: 0 for ap in dfAps['name']}
dicCount["7791-bryancenter-roof-11"] = 0
dicCount["bryancenter-002g-ap3602i-rc-1"] = 0
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

# print(dfRet)
# calculates KDE and decreases the next two intervals accordingly
test1 = 0
dfLeave = pd.read_csv("newLeavingUserCounts/LeavingUserCounts_02_19.csv")
for ind in dfLeave.index:
    if dfLeave['minTime'][ind] <= 1425:
        count = dfLeave['Count'][ind]
        filter = dfRet[dfRet['ap'] == dfLeave.at[ind, 'ap']]
        i = filter[filter['minTime'] == (dfLeave.at[ind, 'minTime']+5)].index.values.astype(int)[0]
        j = filter[filter['minTime'] == (dfLeave.at[ind, 'minTime']+10)].index.values.astype(int)[0]
        # print(dfRet['Count'][i])
        test = dfRet['Count'][i]
        # dfRet['Count'][i] = int(dfRet['Count'][i] - (0.81755435549 * count))
        # dfRet['Count'][j] = int(dfRet['Count'][j] - (0.18244564451 * count))
        dfRet.at[i,'Count'] = int(dfRet.at[i,'Count'] - (0.81755435549 * count))
        dfRet.at[j,'Count'] = int(dfRet.at[j,'Count'] - (0.18244564451 * count))
        # print(dfRet['Count'][i])
        # print("")
        if dfLeave['ap'][ind] == "bryancenter-roof-ap1562d-rw-8":
            test1+= count
            print(count)
            print(test - (0.81755435549 * count))
            print(test)
            print(dfRet['Count'][i])
            print("")
    elif dfLeave['minTime'][ind] == 1430:
        count = dfLeave['Count'][ind]
        filter = dfRet[dfRet['ap'] == dfLeave.at[ind, 'ap']]
        i = filter[filter['minTime'] == (dfLeave.at[ind, 'minTime']+5)].index.values.astype(int)[0]
        j = filter[filter['minTime'] == 1439].index.values.astype(int)[0]
        # dfRet['Count'][i] = int(dfRet['Count'][i] - (0.81755435549 * count))
        # dfRet['Count'][j] = int(dfRet['Count'][j] - (0.18244564451 * count))
        dfRet.at[i,'Count'] = int(dfRet.at[i,'Count'] - (0.81755435549 * count))
        dfRet.at[j,'Count'] = int(dfRet.at[j,'Count'] - (0.18244564451 * count))

print(test1)
# print(dfRet)
# for ind in dfDicCount.index:
#     print("'"+ind+"'" + ",")
#     if ind == ("bryancenter-304-ap3502i-rc-1"):
#         break
dfRet.to_csv("kdeCounts/kdeCounts_02_19.csv")