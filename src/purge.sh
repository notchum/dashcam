#!/usr/bin/env bash

find /media/usb/Recordings/* -type d -ctime +10 | xargs rm -rf
find /media/usb/Logs/* -type d -ctime +10 | xargs rm -rf