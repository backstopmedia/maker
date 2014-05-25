from threading import Thread

from pygame import mixer
mixer.init(frequency=22050, size=-16, channels=2, buffer=512) # config to minimise delays

from bluetooth import *

soundpaths = [
    '/usr/share/sounds/speech-dispatcher/test.wav',
    '/usr/share/sounds/purple/send.wav',
    '/usr/share/sounds/purple/alert.wav',
    '/usr/share/sounds/purple/receive.wav',
    '/usr/share/sounds/freedesktop/stereo/dialog-information.oga',
    '/usr/share/sounds/freedesktop/stereo/audio-volume-change.oga'
]

def reader_loop(reader, index):
    soundindex = index % len(soundpaths)
    soundpath = soundpaths[soundindex]
    sound = mixer.Sound(soundpath)
    while True:
        line = reader.readline().strip()
        if line.startswith("K"):    #look for knocks
            sound.stop()
            sound.play()

def connect_reader(address):
    port = 1    # Guess port (workaround unreadable service record)
    config = (address, port)
    sock = BluetoothSocket()                    
    sock.connect(config)
    return sock.makefile("r",0)

# Look for addresses with these device names 
serialnames = ['linvor','HC-06', 'Slinky']

# Detect bluetooth devices, filtering by name 
readers = [ 
    connect_reader(address) for address in discover_devices() 
    if lookup_name(address) in serialnames
]

# Set up multiple serial streams, managed by their own thread
if len(readers) > 0:

    for (index, reader) in enumerate(readers):
        thread = Thread(                    # spawn new sensor thread
            target=reader_loop,
            args=(reader, index)
        )
        thread.daemon = True    # stop if main thread stops
        thread.start()
        
# If no serial devices detected, report problem
else:
    print "No Serial devices named " + ",".join(serialnames)