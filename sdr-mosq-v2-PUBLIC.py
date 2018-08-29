#!/usr/bin/python3

#********************************************************************
#  sdr-mosq.py
#
#  7 July 2018
#  written by Gerald Swann
#
#  This program reads from an SDR dongle using the excellent rtl_433
#  program and publishes the data using mosquitto_pub
#
#  Unlike the earlier bash script I used, this does not require jq to
#  be installed on the system. Uses instead the python JSON decoder
#
#  The sensors often transmit their data 2 or 3 times.  Using Runme.sh,
#  you would see all the lines in your MQTT data.  This program removes 
#  the duplicate lines
#
#  Copy this python script to your rtl_433 folder
#
#  To see only the MQTT data from this program on your 
#  Home Assistant system, try this command:  
#
#  mosquitto_sub -v -t 'rtl_433/#'  
#
#  Updated 15 july 2018
#  Now, don't publish every code that comes across. At every 30 seconds,
#  they are too frequent.
#  The program variable "between_time" sets minimum time between packets
#********************************************************************

import time
import os
import subprocess
import json
import pdb

#pdb.set_trace()

between_time = 65
# starting clock time of this program
# it's carried in the 'a' array when value
# is published
start = time.time()
#print (time.time())

# list of ID codes, publish topic, and last published time
a = {1779: ["rtl_433/acurite/cha",-120],
     6513: ["rtl_433/acurite/chc",-120],
      -18: ["rtl_433/acurite/ac606tx2",-120],
     -121: ["rtl_433/acurite/ac606tx",-120],
      -59: ["rtl_433/acurite/ac606tx",-120],
        1: ["rtl_433/acurite/rain1",-120],
        2: ["rtl_433/acurite/rain2",-120]}

print (time.time() - start)
print (round(time.time() - start,1))
 
oldLine = "xxx"

with os.popen('../rtl_433/src/rtl_433  -F json -G -U') as sdr:
   for myLine in sdr:
      if myLine != oldLine:
         oldLine = myLine

         # don't print the new line at the end 
#         print(myLine[0:-1],end="  ")
         print(myLine[0:-1])

         decoded = json.loads(str(myLine))

         try:
           print (decoded['sid'],end = " ") 
           myID = decoded['sid']
           if (myID == 0):
              myTopic = "rtl_433/acurite/unk"
         except:         
           myTopic = "x"           

         try:
           if (myTopic == "x"): 
              print (decoded['id'],end =" ")
              myID = decoded['id']
              
#              pdb.set_trace()

              if (myID in a.keys()):
                myTopic = a[myID][0]
                mySeconds = round(time.time() - start,1)
                print (round(mySeconds -  a[myID][1],1), end = "  ")
                if (mySeconds -  a[myID][1] > between_time):
                  print("publishing myID " + str(myID) )
                  a[myID][1] = mySeconds
                  p = subprocess.Popen(["mosquitto_pub","-l","-h","x.x.x.x","-u","xxxx","-P","xxxxxxxx","-t", myTopic ],stdin=subprocess.PIPE)
                  p.communicate(bytes(myLine,'UTF-8'))
                else:
                  print("dropped myID " + str(myID))
                
                myID = "x"  

              else:  
                myTopic = "rtl_433/acurite/unk2"
         except:
              myTopic = "rtl_433/acurite/noid"

         if (myID != "x"):
            print(myTopic)
            p = subprocess.Popen(["mosquitto_pub","-l","-h","x.x.x.x","-u","xxxx","-P",
			"xxxxxxxx","-t", myTopic ],stdin=subprocess.PIPE)
            p.communicate(bytes(myLine,'UTF-8'))
              