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
#  mosquitto_sub -v -t 'rtl_433/#'  -u hass -P hass
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
import socket

#pdb.set_trace()

debug = 0


def checkin():
    # create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'amd1'
    port = 3004
                
    try:
       s.connect((host, port))
       
       # Receive no more than 1024 bytes
       s.sendall(b'mysend')
       msg = s.recv(1024)
       s.close()
       if debug == 1:
           print (msg.decode('ascii'))
    except:
        if debug == 1:
          print('couldnt connect')
                                                                                                 

checkin()

#between_time = 65
between_time = 25
# starting clock time of this program
# it's carried in the 'a' array when value
# is published
start = time.time()
#print (time.time())

# list of ID codes, publish topic, and last published time
from sdrlist import a 

print (time.time() - start)
print (round(time.time() - start,1))
 
oldLine = "xxx"

with os.popen('../rtl_433/build/src/rtl_433  -F json -f 433920000 -G -M level') as sdr:
   for myLine in sdr:
      if myLine != oldLine:
         oldLine = myLine

         # don't print the new line at the end 
#         print(myLine[0:-1])

         decoded = json.loads(str(myLine))

         try:
           print (decoded['sid'],end = " ") 
           myID = decoded['sid']
         except:         
           myID = 999
           myTopic = "x"           

         if (myID == 0):
              myTopic = "rtl_433/acurite/osv1"
              mySeconds = round(time.time() - start,1)
              print (round(mySeconds -  a[myID][1],1), end = "  ")
              if (mySeconds -  a[myID][1] > between_time):
                print ('\033[33;40;1m',end='')
                print("publishing myID " + str(myID) + " " + myTopic )
                print('\033[0m',end='')
                print(myLine[0:-1])
                print("")
              else:  
                print('\033[31m',end='')
                print("dropped myID " + str(myID) + " " + myTopic ) 
                print('\033[0m',end='') 
                print(myLine[0:-1])
                print("")
              checkin()  

         try:
           if (myTopic == "x"): 
              try:  
                print (decoded['id'],end =" ")
                myID = decoded['id']
              except:  
                print(myLine[0:-1])
                raise
                print (decoded['sid'],end =" ")
                myID = decoded['sid']
              
#              pdb.set_trace()

              if (myID in a.keys()):
                myTopic = a[myID][0]
                mySeconds = round(time.time() - start,1)
                print (round(mySeconds -  a[myID][1],1), end = "  ")
                if (mySeconds -  a[myID][1] > between_time):
                   print ('\033[33;40;1m',end='')
                   print("publishing myID " + str(myID) + " " + myTopic )
                   print('\033[0m',end='')
                   print(myLine[0:-1])
                   print("")
                   a[myID][1] = mySeconds
                   p = subprocess.Popen(["mosquitto_pub","-l","-h","192.168.1.40","-u","hass","-P","hass","-t", myTopic ],stdin=subprocess.PIPE)
                   p.communicate(bytes(myLine,'UTF-8'))

#                   checkin()
                else:
                  print('\033[31m',end='')
                  print("dropped myID " + str(myID) + " " + myTopic ) 
                  print('\033[0m',end='') 
                  print(myLine[0:-1])
                  print("")
 
                checkin()
                   
                myID = "x"  

              else:  
                myTopic = "rtl_433/acurite/unk2"
         except:
              raise 
              myTopic = "rtl_433/acurite/noid"

         if (myID != "x"):
            #print("what? " + myTopic)
            # here publish osv1
            p = subprocess.Popen(["mosquitto_pub","-l","-h","192.168.1.40","-u","hass","-P","hass","-t", myTopic ],stdin=subprocess.PIPE)
            p.communicate(bytes(myLine,'UTF-8'))
              