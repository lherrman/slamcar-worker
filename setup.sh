#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive

# Update and upgrade
sudo apt-get update -y
sudo apt-get dist-upgrade -y
sudo apt-get install -y python3-setuptools
# sometimes apache is autoinstalled, let's remove it, we use port 80 ourselves
sudo apt-get remove -y apache2 || true
sudo apt-get autoremove --purge -y

# Activate Camera
wget https://archive.raspberrypi.org/debian/pool/main/r/raspi-config/raspi-config_20220920_all.deb

sudo apt install -y lua5.1 libatopology2 libfftw3-single3 libsamplerate0 alsa-utils ffmpeg
sudo dpkg -i raspi-config_20220920_all.deb
rm -rf raspi-config_20220920_all.deb || true
sudo apt install -y libraspberrypi-bin

sudo mount /dev/mmcblk0p1 /boot || true

if grep -Fxq "start_x=1" /boot/config.txt
then
    echo camera already activated
else
    echo start_x=1 >> /boot/config.txt
fi
raspi-config nonint do_camera 0
raspi-config nonint do_legacy 0

# remove old dependency
sudo killall pigpiod || true
sudo rm -f /usr/local/bin/pigpiod /usr/bin/pigpiod

# Install dependencies
sudo apt-get install -y build-essential i2c-tools avahi-utils joystick git ntp unzip


sudo reboot
