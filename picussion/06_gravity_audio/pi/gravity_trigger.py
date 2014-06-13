import math
import numpy

from threading import Thread

from pygame import mixer
mixer.init(frequency=22050, size=-16, channels=2, buffer=512) # config to minimise delays

from bluetooth import *

# create hotspot class which triggers sounds based on angle between current vector and target vector    
class Hotspot:

    def __init__(self, vector, path):
        self.vector = vector
        self.path = path
        self.matrix = numpy.array(vector)      # turns vector information into matrix for math
        self.sound = mixer.Sound(path)  # turns filepaths into playable samples
        self.active = False
    
    # dot_product of vectors divided by product of magnitude is the cosine of the angle between them
    def get_angle(self, othermatrix): 
        return math.degrees(
            math.acos( 
                self.matrix.dot(othermatrix) / (
                    numpy.sqrt(self.matrix.dot(self.matrix)) * 
                    numpy.sqrt(othermatrix.dot(othermatrix))
                ) 
            )
        )

    # refresh the angle with a new update of accelerometer data
    def update(self, sensor_matrix):
        self.angle = self.get_angle(sensor_matrix)
        if self.is_hot():
            # hotspot should be active
            if not(self.active):
                print "Activate:", self.vector
                self.sound.play()
                self.active = True
        else:
            # hotspot should not be active
            if self.active:
                print "Deactivate  :", self.vector
                self.sound.stop()
                self.active = False
    
    def is_hot(self):
        return self.angle < 30
                
spots = [
    Hotspot([0,0,1],  '/usr/share/sounds/alsa/Front_Center.wav' ),
    Hotspot([0,1,0],  '/usr/share/sounds/alsa/Front_Left.wav'   ),
    Hotspot([1,0,0],  '/usr/share/sounds/alsa/Front_Right.wav'  ),
    Hotspot([0,0,-1], '/usr/share/sounds/alsa/Rear_Center.wav'  ),
    Hotspot([0,-1,0], '/usr/share/sounds/alsa/Rear_Left.wav'    ),
    Hotspot([-1,0,0], '/usr/share/sounds/alsa/Rear_Right.wav'   )
]

# Look for addresses with these device names 
serialnames = ['linvor','HC-06', 'Slinky']

# List bluetooth devices, filtering by name 
def list_available_addresses():
    return [ 
        address for address in discover_devices() 
        if lookup_name(address) in serialnames
    ]

def connect_link(address, modes=("r","w")):
    print("Connecting to " + address)
    port = 1    # Guess port (workaround unreadable service record)
    config = (address, port)
    sock = BluetoothSocket()                    
    sock.connect(config)
    return [sock.makefile(mode,0) for mode in modes]

addresses = list_available_addresses()

# Set up multiple serial streams, managed by their own thread
if len(addresses) > 0:

    # connect to first sensor
    (reader,writer) = connect_link(addresses[0]) 

    
    while True:
        matrix = None
        while matrix == None:
            line = reader.readline()
            if(line[0:2]=="A:"): # detect prefix
                line = line[2:] # remove prefix
                vals = line.split(',') # separate text at commas into values 
                vals = [float(val) for val in vals] # turn text values into integer number values
                matrix = numpy.array(vals)  # turn number values into a matrix
                for spot in spots:
                    spot.update(matrix)

# If no serial devices detected, report problem
else:
    print "No Serial devices named " + ",".join(serialnames)
