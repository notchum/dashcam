#!/usr/bin/env python3

import cv2

def draw_label(img, gps_dict):
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.4
    color = (255, 255, 255)
    thickness = cv2.FILLED
    margin = 2
    pos = (20, 20)
    bg_color = (0, 0, 0)
    text = ""

    if type(gps_dict) is dict:
        text = f"{gps_dict['Date']} {gps_dict['Time']}, Lt: {gps_dict['Latitude']}({gps_dict['LatDirection']}), Lg: {gps_dict['Longitude']}({gps_dict['LongDirection']}), {gps_dict['Speed']} MPH, TC: {gps_dict['TrueCourse']}, Alt: {gps_dict['Altitude']} m"

    txt_size = cv2.getTextSize(text, font_face, scale, thickness)

    end_x = pos[0] + txt_size[0][0] + margin
    end_y = pos[1] - txt_size[0][1] - margin

    img = cv2.rectangle(img, pos, (end_x, end_y), bg_color, thickness)
    img = cv2.putText(img, text, pos, font_face, scale, color, 1, cv2.LINE_AA)

    return img