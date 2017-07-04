## anomaly_detection.py (version 1)

## Script to identify whether a current transaction was substantially higher than previous (T number) of transactions 
## within a soical network with (D number) degress of interaction, for the purpose of notifying other users of interesting purchases.

## Reads in ./log_input/batch_log.json to initialize T and D values (first json object) and establish social network, then reads in 
## ./log_input/stream_log.json to either check whether a purchase was anomalous or change social network. If a purchase was anomalous
## (i.e. greater than 3 standard deviations above mean amount of past transactions), then it is flagged within 
## ./log_input/flagged_purchases.json.

## Written by Dr. Tyler Peel (tpeel21@gmail.com) within Python v3.6.1 64bits, for the Insight program (2017).

#%% libraries
import json
import os
import sys
from math import sqrt 
from collections import OrderedDict

#%% functions
def readData(path, filename): #read json files

    dataLines = []
    
    for line in open(os.path.join(path, filename), "r"):
        dataLines.append(json.loads(line))
    
    return dataLines

def appendData(path, filename, dataLine): #write to json files
    
    with open(os.path.join(path, filename), "a") as json_file:
        json.dump(dataLine, json_file, separators=(', ', ':'))
        
def createFile(path, filename): #create json file
    
    if os.path.isfile(os.path.join(path, filename)):
        os.remove(os.path.join(path, filename))
        
    open(os.path.join(path, filename), "w")

def processData(line, dataLine, eventData, transData, socialData): #create organized lists based on json objects
    event = dataLine["event_type"] 
    
    if event == "purchase":
        amount = dataLine["amount"] 
        user = dataLine["id"] 
        timestamp = dataLine["timestamp"]
        transData.append((user, amount, timestamp, line))
        eventData.append(0) #transaction event
        
    elif event == "befriend":
        user1 = dataLine["id1"] 
        user2 = dataLine["id2"]
        timestamp = dataLine["timestamp"]
        socialData.append((1, user1, user2, timestamp, line))
        eventData.append(1) #social event
        
    elif event == "unfriend":
        user1 = dataLine["id1"] 
        user2 = dataLine["id2"]
        timestamp = dataLine["timestamp"]
        socialData.append((0, user1, user2, timestamp, line))
        eventData.append(1) #social event
        
    
def runSocialState(socialLine, userList, socialState): #create or modify list of users and their friendships
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

    if socialChange == 1: #befriend
        socialState[user1_index].append(user2_index)
        socialState[user2_index].append(user1_index)        
    elif socialChange == 0: #unfriend
        socialState[user1_index].remove(user2_index)
        socialState[user2_index].remove(user1_index)

def find_anomalous_thres(amounts): #compute and return amomalous amount, and mean with sd of past transactions
    mean = (sum(amounts)/len(amounts))
    sd = sqrt(sum((x-mean) ** 2 for x in amounts) / len(amounts))
    
    anomalous_thres = mean + (3 * sd)

    return anomalous_thres, mean, sd
    
def anomalyDetection(D, T, pastTransData, userList, socialState): #first selects relevent users within soical network with D
                                                                  #degrees of interaction then selects past T transactions from 
                                                                  #this network, and returns 1 if current transaction is an anomaly
                                                                  #or 0 if not. This function also returns the amounts for the
                                                                  #current purchase, mean and sd of past T transactions truncated
                                                                  #to 2 decimal places.
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
script_dir = os.path.dirname(os.path.abspath(sys.argv[0])) #directory of python script
parent_dir = os.path.join(script_dir,"..") #parent directory of python script
pastTransData = [] #organized list of past transaction data (user, amount, timestamp, json element # starting at 0)
pastSocialData = [] #organized list of past social data (1=befriend or 0=unfriend, user1, user2, timestamp, 
                    #json element # starting at 0)
pastEventData = [] #1 by n list of whether past data was transaction event (0) or soical event (1)
socialState = [] #list of users within past data and their current friendships, note that users are indexed by appearence as 
                 #documented within the userList variable
userList = [] #1 by n list of user identifications, listed by appearence

#%% main
print("Anomaly detection script running ...")

print("Creating new flagged_purchases file ...")
createFile(os.path.join(parent_dir,"log_output"), "flagged_purchases.json")

print("Reading batch_log ...")
batch_log = readData(os.path.join(parent_dir,"log_input"), "batch_log.json")

D = batch_log[0]["D"] #first line of batch_log sets the flexible D variable, or degrees of interaction within social network
T = batch_log[0]["T"] #first line of batch_log sets the flexible T variable, or past number of transactions for calculations
print("Starting values for D = " + D + ", T = " + T)

print("Processing batch_log ...")
for line in range(1, len(batch_log)):
    processData(line, batch_log[line], pastEventData, pastTransData, pastSocialData)

print("Configuring social network ...")
for line in range(0, len(pastSocialData)):
    runSocialState(pastSocialData[line], userList, socialState)

print("Reading stream_log ...")
stream_log = readData(os.path.join(parent_dir,"log_input"), "stream_log.json")

for line in range(0, len(stream_log)): #process each json object one-by-one
        
    processData(line, stream_log[line], pastEventData, pastTransData, pastSocialData)
    
    if pastEventData[len(pastEventData)-1] == 0: #purchase in json object
        print("Stream #" + str(line) + ": Checking purchase for anomaly")
        [aDet, current_purchase, mean, sd] = anomalyDetection(D, T, pastTransData, userList, socialState)
        
        if aDet == 1:
            print("***Anomalous amount found***")

            dataLine = OrderedDict([("event_type",stream_log[line]["event_type"]), ("timestamp",stream_log[line]["timestamp"]), 
                        ("id",stream_log[line]["id"]), ("amount",stream_log[line]["amount"]), ("mean", mean), ("sd",sd)])
    
            appendData(os.path.join(parent_dir,"log_output"), "flagged_purchases.json", dataLine)
            
    elif pastEventData[len(pastEventData)-1] == 1: #social change in json object
        print("Stream #" + str(line) + ": Change in social network")
        runSocialState(pastSocialData[len(pastSocialData)-1], userList, socialState)
        
        
print("End of stream, ending script ...")
       
    



