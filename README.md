## sdr-mosq
Reads from SDR dongle, maps ID to mosquitto topic and publishes

  sdr-mosq.py

  7 July 2018
  written by Gerald Swann

  This program reads from an SDR dongle using the excellent rtl_433
  program and publishes the data using mosquitto_pub

  Unlike the earlier bash script I used, this does not require jq to
  be installed on the system. Uses instead the python JSON decoder

  The sensors often transmit their data 2 or 3 times.  Using Runme.sh,
  you would see all the lines in your MQTT data.  This program removes 
  the duplicate lines

  Copy this python script to your rtl_433 folder

  To see only the MQTT data from this program on your 
  Home Assistant system, try this command:  

  mosquitto_sub -v -t 'rtl_433/#'
  Updated 15 july 2018
  Now, don't publish every code that comes across. At every 30 seconds,
  they are too frequent.
  The program variable "between_time" sets minimum time between packets
