import math
import numpy

from threading import Thread

from pygame import mixer
mixer.init(frequency=22050, size=-16, channels=2, buffer=512) # minimises delays
from bluetooth import *
from time import sleep

num_links = 2
vectors = [None for link in range(0,num_links)]    

class Synth:
    
    def __init__(self,path,*tests):
        self.path = path
        self.sound = mixer.Sound(path)
        self.tests = tests
        self.active = False
    
    def update(self, vectors):
        if None in vectors: # vectors are not yet all known
            return
        else:
            if False not in [test(*vectors) for test in self.tests]:
                if not self.active:
                    print "Activating " + self.path
                    self.active = True
                    self.set_volume(1)
            else:
                if self.active:
                    print "Deactivating " + self.path
                    self.active = False
                    self.set_volume(0)

    def set_volume(self, vol):
        self.sound.set_volume(vol)

# returns average of several vectors
def between(*vectors):
    return numpy.array([sum(col) / len(vectors) for col in zip(*vectors)])

# vector dot_product divided by product of magnitude=cosine of angle between 
def get_angle(matrix, othermatrix):
    return math.degrees(
        math.acos(
            matrix.dot(othermatrix) / (
                numpy.sqrt(matrix.dot(matrix)) * 
                numpy.sqrt(othermatrix.dot(othermatrix))
            ) 
        )
    )


faces = [
    [0,0,-1.0],
    [0,-1.0,0],
    [-1.0,0,0],
    [0,0,1.0],
    [0,1.0,0],
    [1.0,0,0]
]

# names correspond to sides of the housing (ADXL orientations)
[   
    DOWNSIDE_DOWN, 
    FRONTSIDE_DOWN,
    RIGHTSIDE_DOWN, 
    UPSIDE_DOWN, 
    BACKSIDE_DOWN, 
    LEFTSIDE_DOWN
] = [numpy.array(face) for face in faces]

cone = 30

# Right wrist, Left wrist, both palm downwards
def test_keyboard(left_wrist, right_wrist, left_thigh=BACKSIDE_DOWN):
    return (
        get_angle(right_wrist, DOWNSIDE_DOWN) < cone 
            and
        get_angle(left_wrist, DOWNSIDE_DOWN) < cone
    )

# Right wrist across chest, palm backward, Left wrist palm backward
def test_bass(left_wrist, right_wrist, left_thigh=BACKSIDE_DOWN):
    return (
        get_angle(right_wrist, RIGHTSIDE_DOWN) < cone 
            and
        get_angle(left_wrist, FRONTSIDE_DOWN) < cone
    )

# Right wrist across chest palm backward, Left wrist palm upward    
def test_guitar(left_wrist, right_wrist, left_thigh=BACKSIDE_DOWN):
    return (
        get_angle(right_wrist, RIGHTSIDE_DOWN) < cone 
            and
        get_angle(left_wrist, UPSIDE_DOWN) < cone
    )

# Left wrist and Right wrist each with palm angled 45 degrees down
def test_horns(left_wrist, right_wrist, left_thigh=BACKSIDE_DOWN):
    target_vector = between(FRONTSIDE_DOWN,DOWNSIDE_DOWN)
    return (
        get_angle(right_wrist, target_vector) < cone
            and
        get_angle(left_wrist, target_vector) < cone
    )

# Left wrist across chest, palm backwards, Right wrist downward, palm backwards
def test_handdrum(left_wrist, right_wrist, left_thigh=BACKSIDE_DOWN):
    return (
        get_angle(right_wrist, BACKSIDE_DOWN) < cone 
            and
        get_angle(left_wrist, LEFTSIDE_DOWN) < cone
    )

# Right thigh at 45 degrees
def test_kickdrum(left_wrist, right_wrist, left_thigh=BACKSIDE_DOWN):
    return (
        get_angle(left_thigh,BACKSIDE_DOWN) > cone
    )

# intro sequence is organ, drums (cymbals), tambourine, lead guitar 
synths = [
    Synth("./tracks/Organ, Electric Piano.wav", test_keyboard), 
    Synth("./tracks/Bass.wav", test_bass), 
    Synth("./tracks/Guitar.wav", test_guitar),
    Synth("./tracks/Strings, French Horns.wav", test_horns),
    Synth("./tracks/Tambourine, Congas.wav", test_handdrum),
    Synth("./tracks/Drums.wav", test_kickdrum)
]

# stores sensed gravity vectors and updates program state
def update_vector(index, vector):
    vectors[index] = vector
    for synth in synths:
        synth.update(vectors)

link_addresses = []

# Look for addresses with these device names 
serialnames = ['linvor','HC-06', 'Slinky']

# List bluetooth devices, filtering by name 
def list_available_addresses():
    return [
        address for address in discover_devices() 
        if address not in link_addresses and 
        lookup_name(address) in serialnames
    ]

def connect_link(address, modes=("r","w")):
    print("Connecting to " + address)
    port = 1    # Guess port (workaround unreadable service record)
    config = (address, port)
    sock = BluetoothSocket()                    
    sock.connect(config)
    return [sock.makefile(mode,0) for mode in modes]

def reader_loop(reader, index):
    while True:
        line = reader.readline().strip()
        if(line[0:2]=="A:"):                           # detect prefix
            line = line[2:]                            # remove prefix
            vals = [float(val) for val in line.split(',')] #split text at commas
            update_vector(index, numpy.array(vals))    #turn numbers into matrix

# keep searching until there are enough to link to 
while True:    
    print "Awaiting " + str(num_links - len(link_addresses)) + " links"
    fresh_addresses = list_available_addresses()
    link_addresses.extend(fresh_addresses)
    if len(link_addresses) < num_links :
        sleep(1)        
    else:
        break

# connect to the links
links = [connect_link(address) for address in link_addresses[:num_links]]

print "Connected to all required sensor units, now starting music"

# spawn threads to handle sensor updates
for (index, (reader, writer)) in enumerate(links):
    thread = Thread(                    # spawn new sensor thread
        target=reader_loop,
        args=(reader, index)
    )
    thread.daemon = True                # stop if main thread stops
    thread.start()
    
# trigger sounds on a loop
for synth in synths:
    synth.sound.play(-1)
    synth.sound.set_volume(0)

# wait while sensor readings trigger synths on and off    
while True:
    sleep(0.05)
