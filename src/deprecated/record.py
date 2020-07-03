#!/usr/bin/env python3

import serial
import datetime as dt
from picamera import PiCamera
from gps_utils import parseGPS, createFilenames, convertToMP4
#from img_process import draw_label
from picamera.array import PiRGBArray
import time

# globals
VIDEO_LENGTH = (60 * 0.25) # in seconds
VIDEO_RATE = 25 # framerate

def main():
    port = "/dev/serial0"
    recording_path = "/media/usb/Dashcam/Recordings/"
    logging_path = "/media/usb/Dashcam/Logs/"
    gps_dict = {
        "Date" : "",
        "Time" : "",
        "Latitude"  : "",
        "LatDirection" : "",
        "Longitude" : "",
        "LongDirection" : "",
        "Speed" : "",
        "TrueCourse" : "",
        "Altitude" : ""
    }
    
    # initialize serial port
    ser = serial.Serial(port, baudrate = 9600, timeout = 0.5)

    camera = PiCamera()
    camera.resolution = (1280, 720)
    camera.framerate = 25
    rawCapture = PiRGBArray(camera, size=(1280, 720))

    # allow the camera to warmup
    time.sleep(0.1)

    try:
        while True:
            start = dt.datetime.now()
            record_file, log_file = createFilenames(recording_path, logging_path)
            # start recording using piCamera API
            camera.start_recording(record_file)

            # grab one frame at the time from the stream
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                # grab the raw NumPy array representing the image
                frame = frame.array

                # establish a time for the rest of the logic
                now = dt.datetime.now()

                # detect if video length is reached
                if (now - start).seconds > VIDEO_LENGTH:
                    break

                # Getting GPS data. Converting from bytes to str
                data = ser.readline()
                data = data.decode('ascii', errors='replace').strip()
                #if data[0:6] == "$GNRMC" or data[0:6] == "$GNGGA":
                gps_dict = parseGPS(data, log_file, gps_dict)
                
                # overlay GPS/GLONASS data
                #frame = draw_label(frame, gps_dict)

                # clear the stream in preparation for the next frame
                rawCapture.truncate(0)

            # save the last video file before shutting down
            print("Stopped " + record_file)
            camera.stop_recording()
            print("Converting to MP4...")
            convertToMP4(record_file, VIDEO_RATE)
            print("Finished with recording!")

    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
        print("\nDone.\nExiting.")

if __name__ == "__main__":
    main()