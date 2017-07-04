# Insight_anomaly_detection

anomaly_detection.py (version 1)

Script to identify whether a current transaction was substantially higher than previous (T number) of transactions 
within a soical network with (D number) degress of interaction, for the purpose of notifying other users of interesting purchases.

Reads in ./log_input/batch_log.json to initialize T and D values (first json object) and establish social network, then reads in 
./log_input/stream_log.json to either check whether a purchase was anomalous or change social network. If a purchase was anomalous,
then it is flagged within ./log_input/flagged_purchases.json.

Written by Dr. Tyler Peel (tpeel21@gmail.com) for the Insight program (2017).

##

## Tests

Test_1: this test was provided by the insight program. Demonstrates that program works and directories are correct.

Test_2: test using provided medium-sized dataset. Shows how the script can easily handle large databases.

Test_3: test using provided medium-sized dataset, but D = 4 and T = 100. Illustrates the flexible use of parameters. 
