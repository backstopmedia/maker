from bluetooth import *

from threading import Thread

def connect_sensor(address):
    port = 1    # Guess port (workaround unreadable service record)
    config = (address, port)
    sock = BluetoothSocket()                    
    sock.connect(config)
    return sock.makefile("rw+b",0)

# Look for addresses with these device names 
serialnames = ['linvor','HC-06', 'Slinky']

addresses = [ 
    address for address in discover_devices() 
    if lookup_name(address) in serialnames
]

sensors = [connect_sensor(address) for address in addresses]

def sensor_loop(connection, index):
    while True:
        line = connection.readline().strip()
        print line


for (index, sensor) in enumerate(sensors):
    thread = Thread(                    # spawn new sensor thread
        target=sensor_loop,
        args=(sensor, index)
    )
    thread.daemon = True    # stop if main thread stops
    thread.start()
