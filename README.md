# dashcam
A custom and open-souce dashcam using a Raspberry Pi Zero W with a Pi Camera and a bit of Python code. It records video clips in 10 minute segments, while keeping logs of all GPS/GLONASS data recieved during each recording. The GPS data is overlayed on the output video and any video/logs older than 10 days are deleted.

## Dependencies
- python3
- picamera

## Hardware
- Raspberry Pi Zero W
- [This](https://www.amazon.com/gp/product/B07BTP8VXL/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1) is the camera module I ended up buying. I was attracted to it because of the wide-angle lens, which is great for dashcam footage.
- Considering SD cards are awful at read/writing to a lot, I wanted to use an actual USB flash stick. This also has the benefit of being easily removable to plug into my main PC and copy any needed footage over. Considering this, I bought [this](https://www.digikey.com/product-detail/en/COM-14567/1568-1821-ND/8324538?utm_medium=email&utm_source=oce&utm_campaign=3024_OCE20RT&utm_content=productdetail_US&utm_cid=1175465&so=62943201&mkt_tok=eyJpIjoiWWpGaVlUVm1OalE0TUdZMyIsInQiOiJON1luQmhnckRYVVA2bWRvSFZnNktOZ0lxbHVsZ3Y1WFhJdzlwXC9oaHd1N1k3U05ZTlNhTTFyd2JcL0dMRFBxRmpacHE5WlBxZ3BhcXdXNnpYUDJSVE1iREROdEk3WWFhSnhpS1ZUMVwveGdrRkc2ZHd4WXRVOUx6UTFOWlV0R2FpNyJ9) adapter for the Pi Zero.
- I had an FPV drone GLONASS + GPS unit laying around, [this](https://www.racedayquads.com/products/micro-ublox-m8n-gps-glonass?variant=8730273349739&currency=USD&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&gclid=CjwKCAjwi_b3BRAGEiwAemPNU4GzUlMBN1qUqqBSLWP9ZHq5eBEeStsTBnRZI1SxmPMUBpA9oOqIbBoCoeAQAvD_BwE) one in particular. But really any GPS unit would work.

## 3D Prints
[Here](https://www.thingiverse.com/thing:4518401) are my remixed parts. I printed them out on my Ender 3 and assembled them using some nuts/bolts/screws I had laying around.

## Wiring
The only wiring/soldering that I did to the Pi was for the GPS unit. It is a simple UART interface so I used pins 8 & 10 on the Pi for RX/TX from the unit. Then, for power, I used pin 1 (3V3) and pin 6 (GND).

## Software
1.) [Here](https://desertbot.io/blog/headless-raspberry-pi-4-ssh-wifi-setup) is a great tutorial to set up a headless, lite version of Raspbian.

2.) Clone this repo in the `/home/pi` directory. The tree should look something like this:

```
/home/pi/
└──dashcam/
   ├── crontab.txt
   ├── README.md
   ├── resources/
   └── src/
       ├── deprecated/
       ├── gps_utils.py
       ├── main.py
       └── purge.sh
```

3.) Copy the contents of `crontab.txt` and then run:
```
$ crontab -e
```
During the first run of `crontab` it will ask which text editor to use. After choosing, paste the copied contents of `crontab.txt` and then save/exit. This will run the bash script that purges old folders containing recordings/logs, then runs `main.py` which starts recording/logging.

## Setting Up the USB Stick
There is a particular way to set up the USB to record footage to it. If it isn't set up this way, nothing will work.

### Identify the Devices Unique ID
After plugging the USB stick into the Pi, run the following command:
```
$ ls -l /dev/disk/by-uuid/
```
The output should list some storage devices and unique IDs for each. Look for `sda1` in the output, this is the USB stick. Copy the ID of the stick, it should look something like "18A9-9943".

### Create a Mount Point
Make the mounting directory:
```
$ sudo mkdir /media/usb
```
Then, to ensure the ownership is correct, run the following command:
```
$ sudo chown -R pi:pi /media/usb
```

### Set Up Auto Mount
Usually one could mount the USB and be finished, but since this is a dashcam that will be turning on and off a lot the USB needs to be mounted automatically at each reboot/start-up. To accomplish this, the fstab file needs to be edited (use whatever text editor):
```
$ sudo vim /etc/fstab
```
Then add the following line at the end:
```
UUID=18A9-9943 /media/usb vfat auto,nofail,noatime,users,rw,uid=pi,gid=pi 0 0
```
Make sure to replace the UUID to match the one from earlier. The “nofail” option allows the boot process to proceed if the drive is not plugged in. The “noatime” option stops the file access time being updated every time a file is read from the USB stick. This helps improve performance. After this is done, simply reboot:
```
$ sudo reboot
```

### Set Up Hierarchy
Once the USB is mounting automatically, navigate to `/media/usb` and run:
```
$ mkdir Dashcam/
$ cd Dashcam/
$ mkdir Recordings/ Logs/
```
After creating each directory on the USB stick, the tree should look like:
```
/media/usb/Dashcam/
├── Logs
└── Recordings
```

## Last Notes
- Ignore the `deprecated` folder, I left those files in there because I have commitment issues.
- If you use this project's code then you should alter the video length/framerate/resolution to fit your usage. Furthermore, the purging script checks for folders older than 10 days, this can be altered as well to fit your storage constraints.
- The recordings are initially recording with an `.h264` extension and once the designated video length is reached the script convert the video to `.mp4`. This works pretty well but if the Pi is turned off mid-recording, then the latest file will still have that `.h264` extension, so take note of that.
- The conversion from `.h264` to `.mp4` takes some time to accomplish, so there could be a couple seconds gap in between video clips. Furthermore, if the video length is very large (like 30 minutes) then the conversion will take even longer causing an even larger gap between clips. This conversion function that I used is purely a convenience factor and can be removed if `.h264` video is okay with you. Or if someone wanted to use threads to concurrently convert and start the next recording then that should eliminate these issues.
