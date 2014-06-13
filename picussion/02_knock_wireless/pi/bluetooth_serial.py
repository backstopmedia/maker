from bluetooth import *

def reader_loop(reader):
    while True:
        line = reader.readline().strip()
        print line

# Look for addresses with these device names 
serialnames = ['linvor','HC-06', 'Slinky']

# Detect bluetooth devices, filtering by name 
for address in discover_devices():          # examine each device
    if lookup_name(address) in serialnames: # check its name against the list
        port = 1                            # Guess port, (saves service lookup)
        config = (address, port)            # store the address and port
        sock = BluetoothSocket()
        sock.connect(config)
        bluereader = sock.makefile("r")
        reader_loop(bluereader)
        
# If sensor_loop doesn't block, report problem
print "No Serial devices named " + ",".join(serialnames)
