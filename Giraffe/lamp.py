#!/usr/bin/python

# imports time library for sleep 

import time

# imports random library for random

import random

# imports RPi GPIO library for input/output 

import RPi.GPIO as GPIO

# imports tweepy library for accessing Twiter

import tweepy

# imports pickle library for saving/reading
# a Python object in a file

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

twitterUserName = "twitter user here"

# last message ID and lastMessage string

# load lastMessageID from file giraffe.txt
# if file occurs set lastMessageID to zero
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


# functions
   

def colour(redV, greenV, blueV):
        ''' assign colours to LEDs '''	
	f = open("/dev/pi-blaster", "w") # driver file to be opened
    # next line builds string to assign colours 
	s=("25="+str(redV)+"\n"+"24="+str(greenV)+"\n" "23="+str(blueV)+"\n")
	f.write(s)  # write s to to driver
	f.close()   # close f
    
    
def off():
	''' switch LEDs to off '''
     # assign zero values to red, green and blue channels 
     # to switch them off
	colour(0, 0, 0)

def flash(redV, greenV, blueV):
	''' assign colours and flash 10 times, 1/3 second between off 
    and colour '''	
	flag = True
	i = 0
    
    # adjust the number after 1 to change the number of flashes
	while (i <10 and flashFlag):
		if flag :
			
			colour(redV, greenV, blueV)
			flag = False
		else:
			off()
			flag = True
        # adjust the number after sleep to change 
        # the length of the flashes
		time.sleep(0.33)
		
		i = i + 1

			
def makespaceFlash():
	''' example of two colour flashing using flash function '''	
	off()
	flag = True
	count = 0
    # adjust the number in the while statement 
    # to change the number of flashes
	while (count < 30 and flashFlag): 
		
		if flag :                   # first colours
			red = 1
			green = 0.4
			flag = False
		else :                      # second colours
			red = 0
			green =1
			flag = True

		colour(red, green, 0)       
		# adjust the number to change the length of the flashes
		time.sleep(0.33) 
		
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
    # returns null for any other message and return to cycle colours
			return 
		
def lastMessage(lastMessageID): 
        ''' checks last message returns message text and
        set messageFlag to true if new message '''
        
    # checks messages from twitter user name
	messages = twitter.direct_messages(twitterUserName)
     # searches each message for the latest one
	for message in messages:
		
		messageID = message.id                         
		messageText = message.text
# checks to see if new message if so, prints new message to console        
		if (message.id > lastMessageID):
			print ("*** new message ***" + message.text + " " + str(message.id))
			lastMessageID = message.id                 
			lastMessage = message	                   
		else:
            # messages[0] is the newest message
			lastMessage = messages[0]
			
	# save lastMessageID to file giraffe.txt
	
	file = open('/home/pi/giraffe.txt', 'w') 
	pickle.dump(lastMessageID,file)
	file.close()
	
	# returns the latest message to main program
	
	return lastMessage
	
def my_callback(channel):
	''' button interrupt function, print button press to console when
    called and set flashFlag to False '''
        print ("Button Pressed") 
        global flashFlag         # allows access to the flashFlag flag
        flashFlag = False	     
	

# end of functions

# sets up interrupt for button
GPIO.add_event_detect(7, GPIO.FALLING, callback=my_callback, bouncetime=300)

# Main program

off()                             
# assigns the time to message time minus 75 seconds  
lastMessageTime = time.time() - 75

# main program loop

while True: 
	
	#check Twitter messages, and flash if new message
	
	currentTime = time.time()
	
	checkTime = lastMessageTime + 75 # must be over 70 seconds
	# check if 75 seconds have passed since last check
	if (checkTime <= currentTime):
		oldMessageID = lastMessageID                 
		print("old message ID " + str(oldMessageID))
         #set the time message was checked
		lastMessageTime = time.time()
		print ("checked twitter account for messages")
        # request latest message
		message = lastMessage(oldMessageID) 
		print ("returned ID " + str(message.id))  
        #assign message ID to last Message ID
		lastMessageID = message.id 
		if (oldMessageID == lastMessageID):          
			print ("No New Message")
			
		else:
			print ("*** New Message  ***")           
			messageText = message.text               
			messageFlash(messageText)                
			
	
	# random colours selected every 5 seconds
		
	if (flag): # if flag is set to true update colour

		# assign random value between 0 and 1 for red, 
        # green and blue channels
		
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
    # change number to change time between colour changes
	if elaspsed_time <= 5.0:
		flag = False
		
	else:
		flag = True
        
    # The End  
