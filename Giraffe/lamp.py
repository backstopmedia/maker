#!/usr/bin/python

# imports time library for sleep 

import time

# imports random library for random

import random

# imports RPi GPIO library for input/output 

import RPi.GPIO as GPIO

# imports tweepy library for accessing Twiter

import tweepy

# imports pickle library for saving/reading a Python object in a file

import pickle

# Setup

# set pin 7 as input
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN,pull_up_down=GPIO.PUD_UP)

# twitter account details and set up 

# API keys and access tokens for twitter account
API_key = 'your API key to be placed here'
API_secret = 'your API secret to be placed here'
access_token = 'your access token to be placed here'
access_token_secret = 'your access_token to be placed here'
 
# OAuth process for twitter, using the keys and tokens from above
auth = tweepy.OAuthHandler(API_key, API_secret)
auth.set_access_token(access_token, access_token_secret)
 
# Creation of the actual interface, using authentication
twitter = tweepy.API(auth)

# twitter user name

twitterUserName = ""twitter user here"

# last message ID and lastMessage string

# load lastMessageID from file giraffe.txt if file occurs set lastMessageID to zero
try:
    file = open('/home/pi/giraffe.txt', 'r')
    lastMessageID = pickle.load(file)
    file.close()
except IOError:
    lastMessageID = 0
    file = open('/home/pi/giraffe.txt', 'w')	 
    pickle.dump(lastMessageID,file)
    file.close()

lastMessage = ""

# set flags

flag = True
messageFlag = False
flashFlag = True


# funtions


def colour(redV, greenV, blueV):
        ''' assign colours to LEDs '''	
	f = open("/dev/pi-blaster", "w")                                                 # driver file to be opened
	s=("25=" + str(redV) + "\n" + "24=" + str(greenV) + "\n" "23=" + str(blueV) + "\n") # build string to assign colours 
	f.write(s)                                                                       # write s to to driver
	f.close()                                                                        # close f
    
    
def off():
	''' switch LEDs to off '''
	colour(0, 0, 0) # assign zero values to red, green and blue channels to switch them off

def flash(redV, greenV, blueV):
	''' assign colours and flash 10 times, 1/3 second between off and colour '''	
	flag = True
	i = 0
	while (i <10 and flashFlag):          # adjust the number to change the number of flashes
		if flag :
			
			colour(redV, greenV, blueV)
			flag = False
		else:
			off()
			flag = True

		time.sleep(0.33)                  # adjust the number to change the length of the flashes
		
		i = i + 1

			
def makespaceFlash():
	''' example of two colour flashing using flash function '''	
	off()
	flag = True
	count = 0
	while (count < 30 and flashFlag): # adjust the number to change the number of flashes
		
		if flag :                   # first colours
			red = 1
			green = 0.4
			flag = False
		else :                      # second colours
			red = 0
			green =1
			flag = True

		colour(red, green, 0)       
		
		time.sleep(0.33)            # adjust the number to change the length of the flashes
		
		count = count + 1
		
		
def messageFlash(flashColour): 
	''' selects the correct flash form the message '''
	global flashFlag        # allows access to the flashFlag flag
	flashFlag = True        
	flashColour = flashColour.lower() # converts message to lower-case
	while flashFlag:
		if (flashColour == 'red'):      
			flash(1,0,0)
		elif (flashColour == 'green'):  
			flash(0,1,0)
		elif (flashColour == 'blue'):   
			flash(0,0,1)
		else:
			return # returns null for any other message and return to cycle colours
		
def lastMessage(lastMessageID): 
        ''' checks last message returns message text and set messageFlag to true if new message '''
	messages = twitter.direct_messages(twitterUserName) # checks messages from twitter user name
	for message in messages:                           # searches each message for the latest one
		
		messageID = message.id                         
		messageText = message.text                     
		if (message.id > lastMessageID):               # checks to see if new message if so, prints new message to console
			print ("*** new message ***" + message.text + " " + str(message.id))
			lastMessageID = message.id                 
			lastMessage = message	                   
		else:
			lastMessage = messages[0]                  # messages[0] is the newest message
			
	# save lastMessageID to file giraffe.txt
	
	file = open('/home/pi/giraffe.txt', 'w') 
	pickle.dump(lastMessageID,file)
	file.close()
	
	# returns the latest message to main program
	
	return lastMessage

	
def my_callback(channel):
	''' button interrupt function, print button press to console when called and set flashFlag to False '''
        print ("Button Pressed") 
        global flashFlag         # allows access to the flashFlag flag
        flashFlag = False	     
	

# end of functions

GPIO.add_event_detect(7, GPIO.FALLING, callback=my_callback, bouncetime=300) # sets up interrupt for button

# Main program

off()                               
lastMessageTime = time.time() - 75  # assigns the time to message time minus 75 seconds

# main program loop

while True: 
	
	#check Twitter messages, and flash if new message
	
	currentTime = time.time()
	
	checkTime = lastMessageTime + 75 # must be over 70 seconds
	
	if (checkTime <= currentTime):                   # check if 75 seconds have passed since last check
		oldMessageID = lastMessageID                 
		print("old message ID " + str(oldMessageID)) 
		lastMessageTime = time.time()                #set the time message was checked
		print ("checked twitter account for messages") 
		message = lastMessage(oldMessageID)          # request latest message
		print ("returned ID " + str(message.id))     
		lastMessageID = message.id                   #assign message ID to last Message ID
		if (oldMessageID == lastMessageID):          
			print ("No New Message")
			
		else:
			print ("*** New Message  ***")           
			messageText = message.text               
			messageFlash(messageText)                
			
	
	
	# random colours selected every 5 seconds
		
	if (flag): # if flag is set to true update colour

		# assign random value between 0 and 1 for red, green and blue channels
		
		red = round(random.random(), 3) 
		green = round(random.random(),3)
		blue = round(random.random(),3)
		
		# and then set the RGB colour to the lamp
		
		colour(red, green, blue)
		
		# print out colour values to the console
		
		coloursValues = "Red "+ str(red) + " Green " + str(green) + " Blue " + str(blue)
		print(coloursValues)
		
		# start count down to colour change
	
		start_time = time.time()
		
	elaspsed_time = time.time() - start_time
	if elaspsed_time <= 5.0: # change number to change time between colour changes
		flag = False
		
	else:
		flag = True
        
    # The End  
