# Insight_anomaly_detection

anomaly_detection.py (version 1)

Script to identify whether a current transaction was substantially higher than previous (T number) of transactions 
within a soical network with (D number) degress of interaction, for the purpose of notifying other users of interesting purchases.

Reads in ./log_input/batch_log.json to initialize T and D values (first json object) and establish social network, then reads in 
./log_input/stream_log.json to either check whether a purchase was anomalous or change social network. If a purchase was anomalous,
then it is flagged within ./log_input/flagged_purchases.json.

Written by Dr. Tyler Peel (tpeel21@gmail.com) for the Insight program (2017).
