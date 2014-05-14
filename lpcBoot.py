#!/usr/bin/env python

# 23456789 123456789 123456789 123456789 123456789 123456789 123456789 12345678
# Note - this script must be run as root - do to GPIO and reboot
# 23456789 123456789 123456789 123456789 123456789 123456789 123456789 12345678

import socket
import fcntl
import struct
import functools
import RPi.GPIO as GPIO
import subprocess
from subprocess import call
import flask, flask.views
from time import sleep
import os
import datetime
import netifaces

def get_ip_address(ifname):
    interface = netifaces.ifaddresses(ifname)
    dictLPC = interface.get(netifaces.AF_INET, 'ifnotfound')
    if dictLPC is 'ifnotfound':
        return dictLPC
    else:
        listLPC = dictLPC[0]
        return listLPC.get('addr', 'error')

def setup_mode_update_interfaces():
    with open('/etc/network/interfaces','w') as fi:
        fi.write(
            'auto lo' + "\n" +
            'iface lo inet loopback' + "\n" +
            'iface eth0 inet dhcp' + "\n" +
            'allow-hotplug wlan0' + "\n" + "\n" +
            '#This is the ncommn setup version' + "\n" +
            'iface wlan0 inet static' + "\n" +
            'address 10.10.0.1' + "\n" +
            'netmask 255.255.255.0' + "\n"
        )


def setup_mode_update_dhcpdconf():
    with open('/etc/dhcp/dhcpd.conf','w') as fd:
        fd.write(
            'authoritative;' + "\n" +
            'ddns-update-style none;' + "\n" +
            'default-lease-time 600;' + "\n" +
            'max-lease-time 7200;' + "\n" +
            'log-facility local7;' + "\n" +
            'subnet 10.10.0.0 netmask 255.255.255.0 {' + "\n" +
            'range 10.10.0.25 10.10.0.50;' + "\n"
            'option domain-name-servers 8.8.8.8, 8.8.4.4;' + "\n"
            'option routers 10.10.0.1;' + "\n"
            'interface wlan0;' + "\n"
            '}'
        )

def setup_mode_update_hostapdconf():
    with open('/etc/hostapd/hostapd.conf','w') as fh:
        fh.write(
            'interface=wlan0' + "\n" + 
            'driver=nl80211' + "\n" +
            'ssid=lpcBootStrap' + "\n" + 
            'channel=6' + "\n" +
            'wmm_enabled=1' + "\n" +
            'wpa=1' + "\n" +
            'wpa_passphrase=1234567890' + "\n" +
            'wpa_key_mgmt=WPA-PSK' + "\n" +
            'wpa_pairwise=TKIP' + "\n" +
            'rsn_pairwise=CCMP' + "\n" +
            'auth_algs=1' + "\n" +
            'macaddr_acl=0' + "\n"
        )

def setup_mode_update_hostapd():
    with open('/etc/default/hostapd','w') as fde:
        fde.write(
            'DAEMON_CONF="/etc/hostapd/hostapd.conf"' + "\n"
        )

def setup_mode_update_iscdhcpserver():
    with open('/etc/default/isc-dhcp-server','w') as fs:
        fs.write(
            'DHCPD_CONF=/etc/dhcp/dhcpd.conf' + "\n" +
            'INTERFACES="wlan0"' + "\n"
        )

def setup_mode_update_sound():
    with open('/etc/modules','w') as fm:
        fm.write(
            'snd-bcm2835' + "\n" +
            'amixer cset numid=3 1' + "\n"
        )

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN)
GPIO.setup(11, GPIO.IN)
GPIO.setup(12, GPIO.IN)
GPIO.setup(13, GPIO.IN)
GPIO.setup(15, GPIO.IN)
GPIO.setup(16, GPIO.IN)
GPIO.setup(18, GPIO.IN)

counter = 0

if (GPIO.input(7)== False):
    counter = counter + 1

if (GPIO.input(11)== False):
    counter = counter + 2

if (GPIO.input(12)== False):
    counter = counter + 4

if (GPIO.input(13)== False):
    counter = counter + 8

if (GPIO.input(15)== False):
    counter = counter + 16

if (GPIO.input(16)== False):
    counter = counter + 32

if (GPIO.input(18)== False):
    counter = counter + 64

if (counter == 127 and get_ip_address('wlan0') != '10.10.0.1'):
    setup_mode_update_interfaces()
    setup_mode_update_dhcpdconf()
    setup_mode_update_hostapdconf()
    setup_mode_update_hostapd()
    setup_mode_update_iscdhcpserver()
    setup_mode_update_sound
    call(["reboot"])

if (counter == 127 and get_ip_address('wlan0') == '10.10.0.1'):
    call(["mpg321", "/home/pi/lpc/change_switches.mp3"])
    call(["service", "hostapd", "start"])
    call(["service", "isc-dhcp-server", "start"])
    call(["python", "/home/pi/lpc/lpcWebSetup.py"])
