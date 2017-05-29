#!/usr/bin/env python3
# Author: Andreas Spiess
# Version 1.0.1 20170502 -> shutdown sleep wrong with 100 seconds
#                           and  if ( flagShutDown == True added and GPIO.input(batterySensPin)==0 ):
# Version 1.0.2 20170516 ->  and  if ( flagShutDown == false added and GPIO.input(batterySensPin)==0 ):
#******************************************************************************************************

from pyA20.gpio import gpio
from pyA20.gpio import port
from pyA20.gpio import connector
import os
import time
from time import sleep
import signal
import sys
import logging
import logging.handlers

my_logger = logging.getLogger('PiPowerLogger')
my_logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
my_logger.addHandler(handler)

flagfan        = False
flagShutDown   = False
maxTMP         = 40
fanpin         = port.PG6 # The pin ID, edit here to change it
batterySensPin = port.PG7

def handleFan():
    global flagfan
    CPU_temp = float(getCPUtemperature())
    if CPU_temp>=maxTMP:
        fanON()
        my_logger.critical("pipower: fan on cpu temp:")
        flagfan = True
    if ( CPU_temp < maxTMP-3 ):
	if ( flagfan == True ):
            my_logger.critical("pipower: fan off cpu temp:")
            flagfan = False
        fanOFF()
    return()

def setup():
    gpio.init()
    #setup the port (same as raspberry pi's gpio.setup() function)
    gpio.setcfg(port.PG6, gpio.OUTPUT)
    gpio.setcfg(port.PG7, gpio.INPUT)
    return()

def fanOFF():
    gpio.output(port.PG6, gpio.LOW)
    return()

def fanON():
    gpio.output(port.PG6, gpio.HIGH)
    return()

def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    temp =(res.replace("temp=","").replace("'C\n",""))
    #print("temp is {0}".format(temp)) #Uncomment here for testing
    return temp

def Shutdown(action):  
    fanOFF()
    if( action == 1 ):
        my_logger.critical("pipower: shutdown request:")
        os.system("sudo shutdown -h 1")
    else:
        my_logger.critical("pipower: shutdown cancel:")
        os.system("sudo shutdown -c")
    sleep(10)
    return()

try:
    #print("My raspberry pi pimped...")
    my_logger.debug('pipower: has been initiated')
    total=0
    flagfan = False
    setup() 
    while True:
        sleep(1)
	handleFan()
	if ( flagShutDown == False and  gpio.input(port.PG7) == gpio.LOW):
		print("Pin power was turned to off")
                my_logger.critical('pipower: Pin power was turned to off')
		Shutdown(1)
		flagShutDown = True
        if ( flagShutDown == True and  gpio.input(port.PG7) == gpio.HIGH):
                my_logger.critical('pipower: Pin power was turned to ON')
		print("Pin power was turned to ON")
		Shutdown(0)
                flagShutDown = False
	

except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt 
    fanOFF()
