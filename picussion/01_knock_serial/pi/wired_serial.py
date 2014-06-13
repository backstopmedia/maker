from serial import Serial # Loads the python library for reading serial devices

# Defines a function block called *sensor_loop*, which is invoked by passing it 
# a serial device, and executes a sequence of steps using that device.
def sensor_loop(connection):
    while True: # As long as *True* remains True, in other words forever...
        line = connection.readline() # Read bytes until newline, store in 'line'
        line = line.strip() # Remove leading, trailing whitespace from 'line' 
        print line          # Makes text of the line appear on the console

wiredserial = Serial('/dev/ttyUSB0')# Configure connection called wiredserial
sensor_loop(wiredserial)            # Run steps in sensor_loop using wiredserial
