#!/usr/bin/python3

import pynmea2
import serial
import sys, time, datetime

port = "/dev/serial0"

def logfilename():
    now = datetime.datetime.now()
    return 'NMEA_%0.4d-%0.2d-%0.2d_%0.2d-%0.2d-%0.2d.nmea' % \
                (now.year, now.month, now.day,
                 now.hour, now.minute, now.second)

try:
    while True:
        # read a line of data from the serial port and parse
        with serial.Serial(port, baudrate=9600, timeout=1) as ser:
            # 'warm up' with reading some input
            for i in range(10):
                ser.readline()
            # try to parse (will throw an exception if input is not valid NMEA)
            data = ser.readline()
            if sys.version_info[0] == 3:
                pynmea2.parse(data.decode('ascii', errors='replace'))
            #if data[0:6] == '$GNGGA':
            #    print(data)
        
            # log data
            outfname = logfilename()
            sys.stderr.write('Logging data on %s to %s\n' % (port, outfname))
            with open(outfname, 'wb') as f:
                # loop will exit with Ctrl-C, which raises a
                # KeyboardInterrupt
                while True:
                    line = ser.readline()
                    print(line.decode('ascii', errors='replace').strip())
                    f.write(line)

except (KeyboardInterrupt, SystemExit): # when you press ctrl+c
    sys.stderr.write("\nDone.\nExiting.\n")