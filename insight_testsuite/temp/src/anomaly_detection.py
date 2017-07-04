#%% libraries
import json
import os
import sys
from math import sqrt 
from collections import OrderedDict

#%% functions
def readData(path, filename):

    dataLines = []
    
    for line in open(os.path.join(path, filename), "r"):
        dataLines.append(json.loads(line))
    
    return dataLines

def appendData(path, filename, dataLine):
    
    with open(os.path.join(path, filename), "a") as json_file:
        json.dump(dataLine, json_file, separators=(', ', ':'))
        
def createFile(path, filename):
    
    if os.path.isfile(os.path.join(path, filename)):
        os.remove(os.path.join(path, filename))
        
    open(os.path.join(path, filename), "w")

def processData(line, dataLine, eventData, transData, socialData):
    event = dataLine["event_type"] 
    
    if event == "purchase":
        amount = dataLine["amount"] 
        user = dataLine["id"] 
        timestamp = dataLine["timestamp"]
        transData.append((user, amount, timestamp, line))
        eventData.append(0)
        
    elif event == "befriend":
        user1 = dataLine["id1"] 
        user2 = dataLine["id2"]
        timestamp = dataLine["timestamp"]
        socialData.append((1, user1, user2, timestamp, line))
        eventData.append(1)
        
    elif event == "unfriend":
        user1 = dataLine["id1"] 
        user2 = dataLine["id2"]
        timestamp = dataLine["timestamp"]
        socialData.append((0, user1, user2, timestamp, line))
        eventData.append(1)
        
    
def runSocialState(socialLine, userList, socialState):
    socialChange = socialLine[0]
    user1 = socialLine[1]
    user2 = socialLine[2]
    user1_index = -1
    user2_index = -1
    
    if user1 in userList:
        user1_index = userList.index(user1)
    else:
        userList.append(user1)
        user1_index = len(userList)-1
        socialState.append([user1_index])

    if user2 in userList:
        user2_index = userList.index(user2)
    else:
        userList.append(user2)
        user2_index = len(userList)-1
        socialState.append([user2_index])

    if socialChange == 1:
        socialState[user1_index].append(user2_index)
        socialState[user2_index].append(user1_index)        
    elif socialChange == 0:
        socialState[user1_index].remove(user2_index)
        socialState[user2_index].remove(user1_index)

def find_anomalous_thres(amounts):
    mean = (sum(amounts)/len(amounts))
    sd = sqrt(sum((x-mean) ** 2 for x in amounts) / len(amounts))
    
    anomalous_thres = mean + (3 * sd)

    return anomalous_thres, mean, sd
    
def anomalyDetection(D, T, pastTransData, userList, socialState):
    user = pastTransData[len(pastTransData) - 1][0]
    user_index = -1

    network_indexes = []
    social_network_indexes = []
    social_network = []
    social_network_purchases = []
    current_purchase = []
    selected_purchases = []
        
    if (user in userList) == False:
        userList.append(user)
        user_index = len(userList)-1
        socialState.append([user_index])
      
        
    user_index = userList.index(user)
    social_network_indexes.append(user_index)
            
    for dimensions in range(1, int(D)+1): 
        for numFriend in range(0, len(social_network_indexes)):   
            network_indexes = socialState[social_network_indexes[numFriend]]
            social_network_indexes.extend(network_indexes)
                    
    social_network_indexes = set(social_network_indexes)            
    social_network = list(userList[i] for i in social_network_indexes)

    for line in range(len(pastTransData)-2, -1, -1):
        if pastTransData[line][0] in social_network:     
            social_network_purchases.append(float(pastTransData[line][1]))
            if len(social_network_purchases) > int(T):
                break
    
    current_purchase = float(pastTransData[len(pastTransData)-1][1])
        
    if (len(social_network_purchases) < 2) == False:
        if (len(social_network_purchases) < int(T)) == False:
            selected_purchases = social_network_purchases[0:int(T)]
        else:
            selected_purchases = social_network_purchases[0:len(social_network_purchases)]
        [anomalous_thres, mean, sd] = find_anomalous_thres(selected_purchases)
    else:
         anomalous_thres = 0
         mean = 0
         sd = 0

    if (current_purchase > anomalous_thres) and (anomalous_thres > 0):
        return 1, "%.2f" % current_purchase, "%.2f" % mean, "%.2f" % sd
    else:
        return 0, "%.2f" % current_purchase, "%.2f" % mean, "%.2f" % sd

#%% variables
script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
parent_dir = os.path.join(script_dir,"..") #parent_dir = os.path.join(script_dir) in python console
pastTransData = []
pastSocialData = []
pastEventData = []
socialState = []
userList = []

#%% main
print("Creating new flagged_purchases file ...")
createFile(os.path.join(parent_dir,"log_output"), "flagged_purchases.json")

print("Reading batch_log ...")
batch_log = readData(os.path.join(parent_dir,"log_input"), "batch_log.json")

D = batch_log[0]["D"]
T = batch_log[0]["T"]
print("Starting values for D = " + D + ", T = " + T)

print("Processing batch_log ...")
for line in range(1, len(batch_log)):
    processData(line, batch_log[line], pastEventData, pastTransData, pastSocialData)

print("Configuring social network ...")
for line in range(0, len(pastSocialData)):
    runSocialState(pastSocialData[line], userList, socialState)

print("Reading stream_log ...")
stream_log = readData(os.path.join(parent_dir,"log_input"), "stream_log.json")

for line in range(0, len(stream_log)):
        
    processData(line, stream_log[line], pastEventData, pastTransData, pastSocialData)
    
    if pastEventData[len(pastEventData)-1] == 0:
        print("Stream #" + str(line) + ": Checking purchase for anomaly")
        [aDet, current_purchase, mean, sd] = anomalyDetection(D, T, pastTransData, userList, socialState)
        
        if aDet == 1:
            print("***Anomalous amount found***")

            dataLine = OrderedDict([("event_type",stream_log[line]["event_type"]), ("timestamp",stream_log[line]["timestamp"]), 
                        ("id",stream_log[line]["id"]), ("amount",stream_log[line]["amount"]), ("mean", mean), ("sd",sd)])
    
            appendData(os.path.join(parent_dir,"log_output"), "flagged_purchases.json", dataLine)
            
    elif pastEventData[len(pastEventData)-1] == 1:
        print("Stream # " + str(line) + ": Change in social network")
        runSocialState(pastSocialData[len(pastSocialData)-1], userList, socialState)
        
        
print("End of stream, ending script ...")
       
    



