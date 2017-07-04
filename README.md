# Insight_anomaly_detection

anomaly_detection.py (version 1)

Script to identify whether a current transaction was substantially higher than previous (T number) of transactions 
within a social network with (D number) degress of interaction, for the purpose of notifying other users of interesting purchases.

Reads in ./log_input/batch_log.json to initialize T and D values (first json object) and establish social network, then reads in 
./log_input/stream_log.json to either check whether a purchase was anomalous or change social network. If a purchase was anomalous (i.e. greater than 3 standard deviations above mean amount of past transactions), then it is flagged within ./log_input/flagged_purchases.json.

Written by Dr. Tyler Peel (tpeel21@gmail.com) within Python v3.6.1 64bits, for the Insight program (2017).

## Libraries

json: for reading, writing to json files

os: for producing operating-system-independent pathways

sys: for finding absolute paths of python script

sqrt from math: for computing standard deviation.

OrderedDict from collections: for creating custom python dictionaries for json object

## Tests

Test_1: this test was provided by the insight program. Demonstrates that program works and directories are correct.

Test_2: test using provided medium-sized dataset. Shows how the script can easily handle large databases.

Test_3: test using provided medium-sized dataset, but D = 4 and T = 100. Illustrates the flexible use of parameters. 
