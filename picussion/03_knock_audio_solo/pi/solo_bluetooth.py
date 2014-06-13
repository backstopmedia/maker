from pygame import mixer
mixer.init(frequency=22050, size=-16, channels=2, buffer=512) # config to minimise delays

from bluetooth import *

sound = mixer.Sound('/usr/share/sounds/freedesktop/stereo/complete.oga')

def reader_loop(reader):
    while True:
        line = reader.readline().strip()
        if line.startswith("K"):    #look for knocks
            sound.play()

# Look for addresses with these device names 
serialnames = ['linvor','HC-06', 'Slinky']

# Detect bluetooth devices, filtering by name 
for address in discover_devices():          # examine each device
    if lookup_name(address) in serialnames: # check its name against the list
        port = 1                            # Guess the port (this is a workaround for unreadable RFCOMM service record)
        config = (address, port)            # store the address and port
        sock = BluetoothSocket()
        sock.connect(config)
        bluereader = sock.makefile("r")
        reader_loop(bluereader)
        
# If sensor_loop doesn't block, report problem
print "No Serial devices named " + ",".join(serialnames)