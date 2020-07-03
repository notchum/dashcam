#!/usr/bin/env python3

import os, sys, time, datetime
 
def parseGPS(data, logfile, gps_dict):
    '''
        Takes data as a string from a serial port and parses the **RMC or **GGA NMEA messages.
        If GLONASS then ID should begin with $GN***, if GPS then ID should begin with $GP***.
        Returns a dictionary with all the GPS data.
    '''
    if data[0:6] == "$GNRMC":
        sdata = data.split(",")
        if sdata[2] == 'V':
            err_msg = "ERROR: No satellite data available"
            print(err_msg)
            with open(logfile, 'a') as f:
                f.write(err_msg + '\n')
            return gps_dict
        
        # If data is available then start parsing
        parse_msg = "---Parsing GNRMC---"
        print(parse_msg)
        with open(logfile, 'a') as f:
            f.write(parse_msg + '\n')

        # Grabbing all split data
        time = sdata[1][0:2] + ":" + sdata[1][2:4] + ":" + sdata[1][4:6] # time
        lat = decode(sdata[3])        # latitude
        dirLat = sdata[4]             # latitude direction N/S
        lon = decode(sdata[5])        # longitute
        dirLon = sdata[6]             # longitude direction E/W
        speed = knotsToMPH(sdata[7])  # Speed
        trCourse = sdata[8]           # True course
        date = sdata[9][2:4] + "/" + sdata[9][0:2] + "/" + sdata[9][4:6] # date MM/DD/YY

        # add data to dictionary
        gps_dict["Date"] = date
        gps_dict["Time"] = time
        gps_dict["Latitude"] = lat
        gps_dict["LatDirection"] = dirLat
        gps_dict["Longitude"] = lon
        gps_dict["LongDirection"] = dirLon
        gps_dict["Speed"] = speed
        gps_dict["TrueCourse"] = trCourse
 
        data_string = f"Time : {time}, Latitude : {lat}({dirLat}), Longitude : {lon}({dirLon}), Speed : {speed} MPH, True Course : {trCourse}, Date : {date}"
        print(data_string)

        # log data
        with open(logfile, 'a') as f:
            f.write(data_string + '\n')
    
    elif data[0:6] == "$GNGGA":
        sdata = data.split(",")
        if sdata[6] == '0':
            err_msg = "ERROR: Invalid fix quality"
            print(err_msg)
            with open(logfile, 'a') as f:
                f.write(err_msg + '\n')
            return gps_dict
        elif sdata[6] == '1':
            # If data is available then start parsing
            parse_msg = "---Parsing GNGGA---"
            print(parse_msg)
            with open(logfile, 'a') as f:
                f.write(parse_msg + '\n')

            # Grab the altitude data
            alt = sdata[9] # altitude

            # add data to dictionary
            gps_dict["Altitude"] = alt

            data_string = f"Altitude : {alt}"
            print(data_string)

            # log data
            with open(logfile, 'a') as f:
                f.write(data_string + '\n')

    # TODO: remove this bit, just test
    gps_dict["Date"] = "9/22/2020"
    gps_dict["Time"] = "14:50:48"
    gps_dict["Latitude"] = "50deg 52.1414min"
    gps_dict["LatDirection"] = "N"
    gps_dict["Longitude"] = "50def 05.2949min"
    gps_dict["LongDirection"] = "W"
    gps_dict["Speed"] = "30.8"
    gps_dict["Altitude"] = "85.2"
    gps_dict["TrueCourse"] = "230.9"
    return gps_dict
 
def decode(coord):
    '''
        Converts DDDMM.MMMMM ---> DD deg MM.MMMMM min.
    '''
    x = coord.split(".")
    head = x[0]
    tail = x[1]
    degrees = head[0:-2]
    minutes = head[-2:]
    return degrees + "deg " + minutes + "." + tail + "min"

def knotsToMPH(speed):
    '''
        Converts knots to miles per hour.
    '''
    return speed * 1.15

def createFilenames(recording_path, logging_path):
    '''
        Creates unique files, one for logging and one for recordings.
    '''
    now = datetime.datetime.now()
    date = "%0.4d-%0.2d-%0.2d" % (now.year, now.month, now.day)

    # check if directory with date exists, if not make it
    if not os.path.exists(logging_path + date):
        os.makedirs(logging_path + date)

    log_file = logging_path + date + '/LOG_%0.2dh-%0.2dm-%0.2ds.log' % \
                (now.hour, now.minute, now.second)

    # check if directory with date exists, if not make it
    if not os.path.exists(recording_path + date):
        os.makedirs(recording_path + date)

    record_file = recording_path + date + '/REC_%0.4d-%0.2d-%0.2d_%0.2dh-%0.2dm-%0.2ds.h264' % \
                (now.year, now.month, now.day,
                 now.hour, now.minute, now.second)

    return record_file, log_file


def convertToMP4(filename, framerate):
    '''
        Uses FFMPEG to convert input video to mp4.
    '''
    # Remove the original extension and add mp4 to make output file
    mp4_filename = os.path.splitext(filename)[0] + '.mp4'

    # Run ffmpeg
    os.system("ffmpeg -r " + str(framerate) + " -i " + filename + " -c copy " + mp4_filename)
    
    # Remove old file
    os.remove(filename)