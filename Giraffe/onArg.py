# 
# onArg
#

import sys

# function


def colour(redV, greenV, blueV):
        ''' assign colours to LEDs '''	
        
    # driver file to be opened    
	f = open("/dev/pi-blaster", "w")
    # build string to assign colours 
	s=("25=" + str(redV) + "\n" + "24=" + str(greenV) + "\n" "23=" + str(blueV) + "\n")
    # write s to to driver
	f.write(s)
    # closes driver file
	f.close() 

# main program	

# prints the number of arguments, always return one even if there no arguments
print 'Number of arguments:', len(sys.argv), 'arguments.'
# prints list of the arguments
print 'Argument List:', str(sys.argv)  

# checks if there an argument and asigns it to the channel

if (len(sys.argv) > 1):
	redV = float(sys.argv[1])
else:
	redV = 0
	
if (len(sys.argv) > 2):
	greenV = float(sys.argv[2])
else:
	greenV = 0
	
if (len(sys.argv) > 3):
	blueV = float(sys.argv[3])
else:
	blueV = 0

colour(redV, greenV, blueV) # updates out the colour channels

# The End

	

