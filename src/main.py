#!/usr/bin/env python3

import serial
import datetime as dt
from picamera import PiCamera
from gps_utils import parseGPS, createFilenames, convertToMP4 

# globals
VIDEO_LENGTH = (60 * 10) # in seconds
VIDEO_RATE = 25 # framerate

def main():
    port = "/dev/serial0"
    recording_path = "/media/usb/Dashcam/Recordings/"
    logging_path = "/media/usb/Dashcam/Logs/"
    gps_dict = {
        "Date" : "xx/xx/xxxx",
        "Time" : "xx:xx:xx",
        "Latitude"  : "xxxx",
        "LatDirection" : "x",
        "Longitude" : "xxxx",
        "LongDirection" : "x",
        "Speed" : "xx",
        "TrueCourse" : "xxx",
        "Altitude" : "xxx"
    }
    
    # initialize serial port
    ser = serial.Serial(port, baudrate = 9600, timeout = 0.5)

    # initialize the camera and grab a reference 
    camera = PiCamera() 
    camera.resolution = (1280, 720) 
    camera.framerate = VIDEO_RATE
    camera.start_preview() 

    try: 
        while True:
            start = dt.datetime.now()
            record_file, log_file = createFilenames(recording_path, logging_path)
            # start recording using piCamera API
            camera.start_recording(record_file) 
             
            while (dt.datetime.now() - start).seconds < VIDEO_LENGTH: 
                # Getting GPS data. Converting from bytes to str
                data = ser.readline()
                data = data.decode('ascii', errors='replace').strip()
                if data[0:6] == "$GNRMC" or data[0:6] == "$GNGGA":
                    gps_dict = parseGPS(data, log_file, gps_dict)

                # Overlay the data on each frame
                text = "{} {}, Lt: {}({}), Lg: {}({}), {} MPH, TC: {}, Alt: {} m".format(gps_dict["Date"], gps_dict["Time"], gps_dict["Latitude"], gps_dict["LatDirection"], gps_dict["Longitude"], gps_dict["LongDirection"], gps_dict["Speed"], gps_dict["TrueCourse"], gps_dict["Altitude"])
                camera.annotate_text = text

            print("Stopped " + record_file)
            camera.stop_recording()
            print("Converting to MP4...")
            convertToMP4(record_file, VIDEO_RATE)
            print("Finished with recording!")

    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
        print("\nDone.\nExiting.")

if __name__ == "__main__":
    main()
