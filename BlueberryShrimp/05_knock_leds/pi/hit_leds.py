from random import uniform,randint
from time import time, sleep

from threading import Thread

from pygame import mixer
mixer.init(frequency=22050, size=-16, channels=2, buffer=512) # config to minimise delays

from bluetooth import *

splat_sound = mixer.Sound('splat.wav')
fly_sound = mixer.Sound('fly.wav')

flying  = ( 0.5, 10.0 )
hiding  = ( 0.5,  4.0 )
landing = ( 0.5,  2.0 )

FLY_FLYING = -1
FLY_HIDING = -2

event_due    = -1
fly_volume   = -1
fly_location = FLY_FLYING

def noisy_fly():
    global fly_volume
    if fly_volume == -1 :
        fly_sound.play(loops=-1)
        fly_volume = 0.1
    fly_volume += uniform(-0.1,0.1)
    fly_volume = max(fly_volume, 0.1)
    fly_volume = min(fly_volume, 1.0)
    fly_sound.set_volume(fly_volume)
    
def quiet_fly():
    global fly_volume
    if fly_volume != -1:
        fly_sound.fadeout(250)
        fly_volume = -1

def set_location(new_location):
    global fly_location
    if fly_location != new_location:
        if fly_location >= 0:
            (reader,writer) = sensors[fly_location]
            writer.write("off\n")
        fly_location = new_location
        if fly_location >= 0:
            (reader,writer) = sensors[fly_location]
            writer.write("on\n")

def set_due(new_time):
    global event_due
    event_due = new_time

                
def splat_fly():
    fly_sound.stop()
    splat_sound.play()
    hide_fly()

def land_fly():
    set_location(randint(0,len(sensors) -1))
    set_due(time() + uniform(*landing))

def hide_fly():
    set_location(FLY_HIDING)
    set_due(time() + uniform(*hiding))
    
def launch_fly():    
    set_location(FLY_FLYING)
    set_due(time() + uniform(*flying))

def reader_loop(reader, index):
    while True:
        line = reader.readline().strip()
        if line.startswith("K"):
            if index==fly_location: 
                splat_fly()

def connect_sensor(address, modes=("r","w")):
    port = 1    # Guess port (workaround unreadable service record)
    config = (address, port)
    sock = BluetoothSocket()                    
    sock.connect(config)
    return [sock.makefile(mode,0) for mode in modes]

# Look for addresses with these device names 
serialnames = ['linvor','HC-06', 'Slinky']

# Detect bluetooth devices, filtering by name 
sensors = [ 
    connect_sensor(address) for address in discover_devices() 
    if lookup_name(address) in serialnames
]

# Set up multiple serial streams, managed by their own thread
if len(sensors) > 0:

    for (index, (reader, writer)) in enumerate(sensors):
        thread = Thread(                    # spawn new sensor thread
            target=reader_loop,
            args=(reader, index)
        )
        thread.daemon = True    # stop if main thread stops
        thread.start()
        
    while True:
        if time() > event_due:
            if fly_location == FLY_HIDING:
                launch_fly()
            elif fly_location == FLY_FLYING:
                land_fly()
            elif fly_location >= 0:
                launch_fly()

        if fly_location >= 0 or fly_location == FLY_HIDING:
            quiet_fly()
        elif fly_location == FLY_FLYING:
            noisy_fly()

        sleep(0.05)

# If no serial devices detected, report problem
else:
    print "No Serial devices named " + ",".join(serialnames)