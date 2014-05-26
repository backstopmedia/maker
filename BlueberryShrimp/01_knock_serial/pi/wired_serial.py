from serial import Serial

def sensor_loop(connection):
    while True:
        line = connection.readline()
        line = line.strip()
        print line

wiredserial = Serial('/dev/ttyUSB0')
sensor_loop(wiredserial)